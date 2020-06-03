import os
import logging

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.timesince import timesince

from temba.migrator import Migrator
from temba.orgs.models import TopUp, TopUpCredits, Language
from temba.contacts.models import ContactField, Contact, ContactGroup, ContactURN
from temba.channels.models import Channel, ChannelCount, SyncEvent
from temba.utils import json
from temba.utils.models import TembaModel, generate_uuid

logger = logging.getLogger(__name__)


class MigrationTask(TembaModel):
    STATUS_PENDING = "P"
    STATUS_PROCESSING = "O"
    STATUS_COMPLETE = "C"
    STATUS_FAILED = "F"
    STATUS_CHOICES = (
        (STATUS_PENDING, _("Pending")),
        (STATUS_PROCESSING, _("Processing")),
        (STATUS_COMPLETE, _("Complete")),
        (STATUS_FAILED, _("Failed")),
    )

    org = models.ForeignKey(
        "orgs.Org",
        on_delete=models.PROTECT,
        related_name="%(class)ss",
        help_text=_("The organization of this import progress."),
    )

    migration_org = models.PositiveIntegerField(
        verbose_name=_("Org ID"), help_text=_("The organization ID on live server that is being migrated")
    )

    status = models.CharField(max_length=1, default=STATUS_PENDING, choices=STATUS_CHOICES)

    @classmethod
    def create(cls, org, user, migration_org):
        return cls.objects.create(org=org, migration_org=migration_org, created_by=user, modified_by=user)

    def update_status(self, status):
        self.status = status
        self.save(update_fields=("status", "modified_on"))

    def perform(self):
        self.update_status(self.STATUS_PROCESSING)

        migration_folder = f"{settings.MEDIA_ROOT}/migration_logs"
        if not os.path.exists(migration_folder):
            os.makedirs(migration_folder)

        log_handler = logging.FileHandler(filename=f"{migration_folder}/{self.uuid}.log")
        logger.addHandler(log_handler)
        logger.setLevel("INFO")

        start = timezone.now()

        migrator = Migrator(org_id=self.migration_org)

        logger.info("---------------- Organization ----------------")
        logger.info("[STARTED] Organization data migration")

        org_data = migrator.get_org()
        if not org_data:
            logger.info("[ERROR] No organization data found")
            self.update_status(self.STATUS_FAILED)
            return

        self.update_org(org_data)
        logger.info("[COMPLETED] Organization data migration")
        logger.info("")

        logger.info("---------------- TopUps ----------------")
        logger.info("[STARTED] TopUps migration")

        # Inactivating all org topups before importing the ones from Live server
        TopUp.objects.filter(is_active=True, org=self.org).update(is_active=False)

        org_topups = migrator.get_org_topups()
        if org_topups:
            self.add_topups(logger=logger, topups=org_topups, migrator=migrator)

        logger.info("[COMPLETED] TopUps migration")
        logger.info("")

        logger.info("---------------- Languages ----------------")
        logger.info("[STARTED] Languages migration")

        # Inactivating all org languages before importing the ones from Live server
        self.org.primary_language = None
        self.org.save(update_fields=["primary_language"])

        Language.objects.filter(is_active=True, org=self.org).delete()

        org_languages = migrator.get_org_languages()
        if org_languages:
            self.add_languages(logger=logger, languages=org_languages)

            if org_data.primary_language_id:
                org_primary_language = MigrationAssociation.get_new_object(
                    model=MigrationAssociation.MODEL_ORG_LANGUAGE, old_id=org_data.primary_language_id
                )
                self.org.primary_language = org_primary_language
                self.org.save(update_fields=["primary_language"])

        logger.info("[COMPLETED] Languages migration")
        logger.info("")

        logger.info("---------------- Channels ----------------")
        logger.info("[STARTED] Channels migration")

        # Inactivating all org channels before importing the ones from Live server
        existing_channels = Channel.objects.filter(org=self.org)
        for channel in existing_channels:
            channel.uuid = generate_uuid()
            channel.secret = None
            channel.save(update_fields=["uuid", "secret"])
            channel.release(deactivate=False)

        org_channels = migrator.get_org_channels()
        if org_channels:
            self.add_channels(logger=logger, channels=org_channels, migrator=migrator)

        logger.info("[COMPLETED] Channels migration")
        logger.info("")

        logger.info("---------------- Contact Fields ----------------")
        logger.info("[STARTED] Contact Fields migration")

        org_contact_fields = migrator.get_org_contact_fields()
        if org_contact_fields:
            self.add_contact_fields(logger=logger, fields=org_contact_fields)

        logger.info("[COMPLETED] Contact Fields migration")
        logger.info("")

        logger.info("---------------- Contacts ----------------")
        logger.info("[STARTED] Contacts migration")

        org_contacts = migrator.get_org_contacts()
        if org_contacts:
            self.add_contacts(logger=logger, contacts=org_contacts)

        logger.info("[COMPLETED] Contacts migration")
        logger.info("")

        logger.info("---------------- Contact Groups ----------------")
        logger.info("[STARTED] Contact Groups migration")

        org_contact_groups = migrator.get_org_contact_groups()
        if org_contact_groups:
            self.add_contact_groups(logger=logger, groups=org_contact_groups, migrator=migrator)

        logger.info("[COMPLETED] Contact Groups migration")
        logger.info("")

        elapsed = timesince(start)
        logger.info(f"This process took {elapsed}")

        self.update_status(self.STATUS_COMPLETE)

        self.remove_association()

    def update_org(self, org_data):
        self.org.plan = org_data.plan
        self.org.plan_start = org_data.plan_start
        self.org.stripe_customer = org_data.stripe_customer
        self.org.language = org_data.language
        self.org.timezone = org_data.timezone
        self.org.date_format = org_data.date_format
        self.org.config = json.loads(org_data.config) if org_data.config else dict()
        self.org.is_anon = org_data.is_anon
        self.org.surveyor_password = org_data.surveyor_password
        self.org.parent_id = org_data.parent_id
        self.org.save(
            update_fields=[
                "plan",
                "plan_start",
                "stripe_customer",
                "language",
                "timezone",
                "date_format",
                "config",
                "is_anon",
                "surveyor_password",
                "parent_id",
            ]
        )

    def add_topups(self, logger, topups, migrator):
        for topup in topups:
            logger.info(f">>> TopUp: {topup.id} - {topup.credits}")
            new_topup = TopUp.create(
                user=self.created_by,
                price=topup.price,
                credits=topup.credits,
                org=self.org,
                expires_on=topup.expires_on,
            )

            MigrationAssociation.create(
                migration_task=self, old_id=topup.id, new_id=new_topup.id, model=MigrationAssociation.MODEL_ORG_TOPUP
            )

            org_topup_credits = migrator.get_org_topups_credit(topup_id=topup.id)
            for topup_credit in org_topup_credits:
                TopUpCredits.objects.create(
                    topup=new_topup, used=topup_credit.used, is_squashed=topup_credit.is_squashed
                )

    def add_languages(self, logger, languages):
        for language in languages:
            logger.info(f">>> Language: {language.id} - {language.name}")

            new_language = Language.create(
                org=self.org, user=self.created_by, name=language.name, iso_code=language.iso_code
            )

            MigrationAssociation.create(
                migration_task=self,
                old_id=language.id,
                new_id=new_language.id,
                model=MigrationAssociation.MODEL_ORG_LANGUAGE,
            )

    def add_channels(self, logger, channels, migrator):
        for channel in channels:
            logger.info(f">>> Channel: {channel.id} - {channel.name}")

            channel_type = channel.channel_type

            channel_config = json.loads(channel.config) if channel.config else dict()

            if channel_type == "WS":
                # Changing type for WebSocket channel
                channel_type = "WCH"
            elif channel_type == "FB" and channel.secret:
                # Adding channel secret when it is a Facebook channel to channel config field
                channel_config[Channel.CONFIG_SECRET] = channel.secret

            if isinstance(channel_type, str):
                channel_type = Channel.get_type_from_code(channel_type)

            schemes = channel_type.schemes

            new_channel = Channel.objects.create(
                org=self.org,
                created_by=self.created_by,
                modified_by=self.created_by,
                country=channel.country,
                channel_type=channel_type.code,
                name=channel.name or channel.address,
                address=channel.address,
                config=channel_config,
                role=channel.role,
                schemes=schemes,
                uuid=channel.uuid,
                claim_code=channel.claim_code,
                secret=channel.secret,
                last_seen=channel.last_seen,
                device=channel.device,
                os=channel.os,
                alert_email=channel.alert_email,
                bod=channel.bod,
                tps=settings.COURIER_DEFAULT_TPS,
            )

            MigrationAssociation.create(
                migration_task=self,
                old_id=channel.id,
                new_id=new_channel.id,
                model=MigrationAssociation.MODEL_CHANNEL,
            )

            channel_counts = migrator.get_channels_count(channel_id=channel.id)
            for channel_count in channel_counts:
                ChannelCount.objects.create(
                    channel=new_channel,
                    count_type=channel_count.count_type,
                    day=channel_count.day,
                    count=channel_count.count,
                    is_squashed=channel_count.is_squashed,
                )

            # If the channel is an Android channel it will migrate the sync events
            if channel_type.code == "A":
                channel_syncevents = migrator.get_channel_syncevents(channel_id=channel.id)
                for channel_syncevent in channel_syncevents:
                    SyncEvent.objects.create(
                        created_by=self.created_by,
                        modified_by=self.created_by,
                        channel=new_channel,
                        power_source=channel_syncevent.power_source,
                        power_status=channel_syncevent.power_status,
                        power_level=channel_syncevent.power_level,
                        network_type=channel_syncevent.network_type,
                        lifetime=channel_syncevent.lifetime,
                        pending_message_count=channel_syncevent.pending_message_count,
                        retry_message_count=channel_syncevent.retry_message_count,
                        incoming_command_count=channel_syncevent.incoming_command_count,
                        outgoing_command_count=channel_syncevent.outgoing_command_count,
                    )

    def add_contact_fields(self, logger, fields):
        for field in fields:
            logger.info(f">>> Contact Field: {field.id} - {field.label}")

            new_contact_field = ContactField.get_or_create(
                user=self.created_by,
                org=self.org,
                key=field.key,
                label=field.label,
                show_in_table=field.show_in_table,
                value_type=field.value_type,
            )
            if field.uuid != new_contact_field.uuid:
                new_contact_field.uuid = field.uuid
                new_contact_field.save(update_fields=["uuid"])

            MigrationAssociation.create(
                migration_task=self,
                old_id=field.id,
                new_id=new_contact_field.id,
                model=MigrationAssociation.MODEL_CONTACT_FIELD,
            )

    def add_contacts(self, logger, contacts):
        for contact in contacts:
            logger.info(f">>> Contact: {contact.uuid} - {contact.name}")

            existing_contact = Contact.objects.filter(uuid=contact.uuid, org=self.org).first()
            if not existing_contact:
                existing_contact = Contact.objects.create(
                    org=self.org,
                    created_by=self.created_by,
                    modified_by=self.created_by,
                    name=contact.name,
                    language=contact.language,
                    is_blocked=contact.is_blocked,
                    is_stopped=contact.is_stopped,
                    is_active=contact.is_active,
                    uuid=contact.uuid,
                )

            MigrationAssociation.create(
                migration_task=self,
                old_id=contact.id,
                new_id=existing_contact.id,
                model=MigrationAssociation.MODEL_CONTACT,
            )

    def add_contact_groups(self, logger, groups, migrator):
        for group in groups:
            logger.info(f">>> Contact Group: {group.uuid} - {group.name}")

            contact_group = ContactGroup.get_or_create(
                org=self.org,
                user=self.created_by,
                name=group.name,
                query=group.query,
                uuid=group.uuid,
            )

            # Making sure that the uuid will be the same from live server
            if contact_group.uuid != group.uuid:
                contact_group.uuid = group.uuid
                contact_group.save(update_fields=["uuid"])

            MigrationAssociation.create(
                migration_task=self,
                old_id=group.id,
                new_id=contact_group.id,
                model=MigrationAssociation.MODEL_CONTACT_GROUP,
            )

            contactgroup_contacts = migrator.get_contactgroups_contacts(contactgroup_id=group.id)
            for item in contactgroup_contacts:
                new_contact_obj = MigrationAssociation.get_new_object(
                    model=MigrationAssociation.MODEL_CONTACT,
                    old_id=item.contact_id,
                )
                if new_contact_obj and not contact_group.is_dynamic:
                    contact_group.update_contacts(user=self.created_by, contacts=[new_contact_obj], add=True)

    def remove_association(self):
        self.associations.all().delete()


class MigrationAssociation(models.Model):
    MODEL_CAMPAIGN = "campaigns_campaign"
    MODEL_CAMPAIGN_EVENT = "campaigns_campaignevent"
    MODEL_CHANNEL = "channels_channel"
    MODEL_CONTACT = "contacts_contact"
    MODEL_CONTACT_URN = "contacts_contacturn"
    MODEL_CONTACT_GROUP = "contacts_contactgroup"
    MODEL_CONTACT_FIELD = "contacts_contactfield"
    MODEL_MSG = "msgs_msg"
    MODEL_MSG_LABEL = "msgs_label"
    MODEL_FLOW = "flows_flow"
    MODEL_FLOW_LABEL = "flows_flowlabel"
    MODEL_FLOW_RUN = "flows_flowrun"
    MODEL_FLOW_START = "flows_flowstart"
    MODEL_LINK = "links_link"
    MODEL_SCHEDULE = "schedules_schedule"
    MODEL_ORG_TOPUP = "orgs_topups"
    MODEL_ORG_LANGUAGE = "orgs_language"
    MODEL_TRIGGER = "triggers_trigger"

    MODEL_CHOICES = (
        (MODEL_CAMPAIGN, MODEL_CAMPAIGN),
        (MODEL_CAMPAIGN_EVENT, MODEL_CAMPAIGN_EVENT),
        (MODEL_CHANNEL, MODEL_CHANNEL),
        (MODEL_CONTACT, MODEL_CONTACT),
        (MODEL_CONTACT_URN, MODEL_CONTACT_URN),
        (MODEL_CONTACT_GROUP, MODEL_CONTACT_GROUP),
        (MODEL_CONTACT_FIELD, MODEL_CONTACT_FIELD),
        (MODEL_MSG, MODEL_MSG),
        (MODEL_MSG_LABEL, MODEL_MSG_LABEL),
        (MODEL_FLOW, MODEL_FLOW),
        (MODEL_FLOW_LABEL, MODEL_FLOW_LABEL),
        (MODEL_FLOW_RUN, MODEL_FLOW_RUN),
        (MODEL_FLOW_START, MODEL_FLOW_START),
        (MODEL_LINK, MODEL_LINK),
        (MODEL_SCHEDULE, MODEL_SCHEDULE),
        (MODEL_ORG_TOPUP, MODEL_ORG_TOPUP),
        (MODEL_ORG_LANGUAGE, MODEL_ORG_LANGUAGE),
        (MODEL_TRIGGER, MODEL_TRIGGER),
    )

    migration_task = models.ForeignKey(MigrationTask, on_delete=models.CASCADE, related_name="associations")

    old_id = models.PositiveIntegerField(verbose_name=_("The ID provided from live server"))

    new_id = models.PositiveIntegerField(verbose_name=_("The new ID generated on app server"))

    model = models.CharField(verbose_name=_("Model related to the ID"), max_length=255, choices=MODEL_CHOICES)

    def __str__(self):
        return self.model

    @classmethod
    def create(cls, migration_task, old_id, new_id, model):
        return MigrationAssociation.objects.create(
            migration_task=migration_task, old_id=old_id, new_id=new_id, model=model
        )

    @classmethod
    def get_new_object(cls, model, old_id):
        obj = (
            MigrationAssociation.objects.filter(old_id=old_id, model=model)
            .only("new_id", "migration_task__org")
            .select_related("migration_task")
            .first()
        )

        if not obj:
            logger.warning(f"[WARNING] No object found on get_new_object method [table: {model}, id: {old_id}]")
            return None

        _model = obj.get_related_model()
        if not _model:
            logger.error("[ERROR] No model class found on get_new_object method")
            return None

        return _model.objects.filter(id=obj.new_id, org=obj.migration_task.org).first()

    def get_related_model(self):
        from temba.campaigns.models import Campaign, CampaignEvent
        from temba.msgs.models import Msg, Label
        from temba.flows.models import Flow, FlowLabel, FlowRun, FlowStart
        from temba.links.models import Link
        from temba.schedules.models import Schedule
        from temba.triggers.models import Trigger

        model_class = {
            MigrationAssociation.MODEL_CAMPAIGN: Campaign,
            MigrationAssociation.MODEL_CAMPAIGN_EVENT: CampaignEvent,
            MigrationAssociation.MODEL_CHANNEL: Channel,
            MigrationAssociation.MODEL_CONTACT: Contact,
            MigrationAssociation.MODEL_CONTACT_URN: ContactURN,
            MigrationAssociation.MODEL_CONTACT_GROUP: ContactGroup,
            MigrationAssociation.MODEL_CONTACT_FIELD: ContactField,
            MigrationAssociation.MODEL_MSG: Msg,
            MigrationAssociation.MODEL_MSG_LABEL: Label,
            MigrationAssociation.MODEL_FLOW: Flow,
            MigrationAssociation.MODEL_FLOW_LABEL: FlowLabel,
            MigrationAssociation.MODEL_FLOW_RUN: FlowRun,
            MigrationAssociation.MODEL_FLOW_START: FlowStart,
            MigrationAssociation.MODEL_LINK: Link,
            MigrationAssociation.MODEL_SCHEDULE: Schedule,
            MigrationAssociation.MODEL_ORG_TOPUP: TopUp,
            MigrationAssociation.MODEL_ORG_LANGUAGE: Language,
            MigrationAssociation.MODEL_TRIGGER: Trigger,
        }
        return model_class.get(self.model, None)