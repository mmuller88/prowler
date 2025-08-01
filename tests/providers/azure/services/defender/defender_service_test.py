from datetime import timedelta
from unittest.mock import patch

from prowler.providers.azure.services.defender.defender_service import (
    Assesment,
    AutoProvisioningSetting,
    Defender,
    IoTSecuritySolution,
    Pricing,
    SecurityContactConfiguration,
    Setting,
)
from tests.providers.azure.azure_fixtures import (
    AZURE_SUBSCRIPTION_ID,
    set_mocked_azure_provider,
)


def mock_defender_get_pricings(_):
    return {
        AZURE_SUBSCRIPTION_ID: {
            "Standard": Pricing(
                resource_id="resource_id",
                resource_name="resource_name",
                pricing_tier="pricing_tier",
                free_trial_remaining_time=timedelta(days=1),
                extensions={},
            )
        }
    }


def mock_defender_get_auto_provisioning_settings(_):
    return {
        AZURE_SUBSCRIPTION_ID: {
            "default": AutoProvisioningSetting(
                resource_id="/subscriptions/resource_id",
                resource_name="default",
                resource_type="Microsoft.Security/autoProvisioningSettings",
                auto_provision="On",
            )
        }
    }


def mock_defender_get_assessments(_):
    return {
        AZURE_SUBSCRIPTION_ID: {
            "default": Assesment(
                resource_id="/subscriptions/resource_id",
                resource_name="default",
                status="Healthy",
            )
        }
    }


def mock_defender_get_security_contacts(*args, **kwargs):
    from prowler.providers.azure.services.defender.defender_service import (
        NotificationsByRole,
    )

    return {
        AZURE_SUBSCRIPTION_ID: {
            "/subscriptions/resource_id": SecurityContactConfiguration(
                id="/subscriptions/resource_id",
                name="default",
                enabled=True,
                emails=["user@user.com", "test@test.es"],
                phone="666666666",
                notifications_by_role=NotificationsByRole(
                    state=True, roles=["Owner", "Contributor"]
                ),
                alert_minimal_severity="High",
                attack_path_minimal_risk_level=None,
            )
        }
    }


def mock_defender_get_settings(_):
    return {
        AZURE_SUBSCRIPTION_ID: {
            "MCAS": Setting(
                resource_id="/subscriptions/resource_id",
                resource_type="Microsoft.Security/locations/settings",
                kind="DataExportSettings",
                enabled=True,
            )
        }
    }


def mock_defender_get_iot_security_solutions(_):
    return {
        AZURE_SUBSCRIPTION_ID: {
            "/subscriptions/resource_id": IoTSecuritySolution(
                resource_id="/subscriptions/resource_id",
                name="iot_sec_solution",
                status="Enabled",
            )
        }
    }


@patch(
    "prowler.providers.azure.services.defender.defender_service.Defender._get_pricings",
    new=mock_defender_get_pricings,
)
@patch(
    "prowler.providers.azure.services.defender.defender_service.Defender._get_auto_provisioning_settings",
    new=mock_defender_get_auto_provisioning_settings,
)
@patch(
    "prowler.providers.azure.services.defender.defender_service.Defender._get_assessments",
    new=mock_defender_get_assessments,
)
@patch(
    "prowler.providers.azure.services.defender.defender_service.Defender._get_settings",
    new=mock_defender_get_settings,
)
@patch(
    "prowler.providers.azure.services.defender.defender_service.Defender._get_security_contacts",
    new=mock_defender_get_security_contacts,
)
@patch(
    "prowler.providers.azure.services.defender.defender_service.Defender._get_iot_security_solutions",
    new=mock_defender_get_iot_security_solutions,
)
class Test_Defender_Service:
    def test_get_client(self):
        defender = Defender(set_mocked_azure_provider())
        assert (
            defender.clients[AZURE_SUBSCRIPTION_ID].__class__.__name__
            == "SecurityCenter"
        )

    def test__get_subscriptions__(self):
        defender = Defender(set_mocked_azure_provider())
        defender = Defender(set_mocked_azure_provider())
        assert defender.subscriptions.__class__.__name__ == "dict"

    def test_get_pricings(self):
        defender = Defender(set_mocked_azure_provider())
        assert len(defender.pricings) == 1
        assert (
            defender.pricings[AZURE_SUBSCRIPTION_ID]["Standard"].resource_id
            == "resource_id"
        )
        assert (
            defender.pricings[AZURE_SUBSCRIPTION_ID]["Standard"].resource_name
            == "resource_name"
        )
        assert (
            defender.pricings[AZURE_SUBSCRIPTION_ID]["Standard"].pricing_tier
            == "pricing_tier"
        )
        assert defender.pricings[AZURE_SUBSCRIPTION_ID][
            "Standard"
        ].free_trial_remaining_time == timedelta(days=1)
        assert defender.pricings[AZURE_SUBSCRIPTION_ID]["Standard"].extensions == {}

    def test_get_auto_provisioning_settings(self):
        defender = Defender(set_mocked_azure_provider())
        assert len(defender.auto_provisioning_settings) == 1
        assert (
            defender.auto_provisioning_settings[AZURE_SUBSCRIPTION_ID][
                "default"
            ].resource_id
            == "/subscriptions/resource_id"
        )
        assert (
            defender.auto_provisioning_settings[AZURE_SUBSCRIPTION_ID][
                "default"
            ].resource_name
            == "default"
        )
        assert (
            defender.auto_provisioning_settings[AZURE_SUBSCRIPTION_ID][
                "default"
            ].resource_type
            == "Microsoft.Security/autoProvisioningSettings"
        )
        assert (
            defender.auto_provisioning_settings[AZURE_SUBSCRIPTION_ID][
                "default"
            ].auto_provision
            == "On"
        )

    def test_get_assessments(self):
        defender = Defender(set_mocked_azure_provider())
        assert len(defender.assessments) == 1
        assert (
            defender.assessments[AZURE_SUBSCRIPTION_ID]["default"].resource_id
            == "/subscriptions/resource_id"
        )
        assert (
            defender.assessments[AZURE_SUBSCRIPTION_ID]["default"].resource_name
            == "default"
        )
        assert (
            defender.assessments[AZURE_SUBSCRIPTION_ID]["default"].status == "Healthy"
        )

    def test_get_settings(self):
        defender = Defender(set_mocked_azure_provider())
        assert len(defender.settings) == 1
        assert (
            defender.settings[AZURE_SUBSCRIPTION_ID]["MCAS"].resource_id
            == "/subscriptions/resource_id"
        )
        assert (
            defender.settings[AZURE_SUBSCRIPTION_ID]["MCAS"].resource_type
            == "Microsoft.Security/locations/settings"
        )
        assert (
            defender.settings[AZURE_SUBSCRIPTION_ID]["MCAS"].kind
            == "DataExportSettings"
        )
        assert defender.settings[AZURE_SUBSCRIPTION_ID]["MCAS"].enabled

    def test_get_security_contacts(self):
        defender = Defender(set_mocked_azure_provider())
        assert len(defender.security_contact_configurations) == 1
        contact = defender.security_contact_configurations[AZURE_SUBSCRIPTION_ID][
            "/subscriptions/resource_id"
        ]
        assert contact.id == "/subscriptions/resource_id"
        assert contact.name == "default"
        assert contact.emails == ["user@user.com", "test@test.es"]
        assert contact.phone == "666666666"
        assert contact.alert_minimal_severity == "High"
        assert contact.notifications_by_role.state is True
        assert contact.notifications_by_role.roles == ["Owner", "Contributor"]

    def test_get_iot_security_solutions(self):
        defender = Defender(set_mocked_azure_provider())
        assert len(defender.iot_security_solutions) == 1
        assert (
            defender.iot_security_solutions[AZURE_SUBSCRIPTION_ID][
                "/subscriptions/resource_id"
            ].resource_id
            == "/subscriptions/resource_id"
        )
        assert (
            defender.iot_security_solutions[AZURE_SUBSCRIPTION_ID][
                "/subscriptions/resource_id"
            ].name
            == "iot_sec_solution"
        )
        assert (
            defender.iot_security_solutions[AZURE_SUBSCRIPTION_ID][
                "/subscriptions/resource_id"
            ].status
            == "Enabled"
        )
