import yaml
from mock import MagicMock

from prowler.providers.m365.lib.mutelist.mutelist import M365Mutelist
from tests.lib.outputs.fixtures.fixtures import generate_finding_output

MUTELIST_FIXTURE_PATH = "tests/providers/m365/lib/mutelist/fixtures/m365_mutelist.yaml"


class TestM365Mutelist:
    def test_get_mutelist_file_from_local_file(self):
        mutelist = M365Mutelist(mutelist_path=MUTELIST_FIXTURE_PATH)

        with open(MUTELIST_FIXTURE_PATH) as f:
            mutelist_fixture = yaml.safe_load(f)["Mutelist"]

        assert mutelist.mutelist == mutelist_fixture
        assert mutelist.mutelist_file_path == MUTELIST_FIXTURE_PATH

    def test_get_mutelist_file_from_local_file_non_existent(self):
        mutelist_path = "tests/lib/mutelist/fixtures/not_present"
        mutelist = M365Mutelist(mutelist_path=mutelist_path)

        assert mutelist.mutelist == {}
        assert mutelist.mutelist_file_path == mutelist_path

    def test_validate_mutelist_not_valid_key(self):
        mutelist_path = MUTELIST_FIXTURE_PATH
        with open(mutelist_path) as f:
            mutelist_fixture = yaml.safe_load(f)["Mutelist"]

        mutelist_fixture["Accounts1"] = mutelist_fixture["Accounts"]
        del mutelist_fixture["Accounts"]

        mutelist = M365Mutelist(mutelist_content=mutelist_fixture)

        assert len(mutelist.validate_mutelist(mutelist_fixture)) == 0
        assert mutelist.mutelist == {}
        assert mutelist.mutelist_file_path is None

    def test_is_finding_muted(self):
        # Mutelist
        mutelist_content = {
            "Accounts": {
                "subscription_1": {
                    "Checks": {
                        "check_test": {
                            "Regions": ["*"],
                            "Resources": ["test_resource"],
                        }
                    }
                }
            }
        }

        mutelist = M365Mutelist(mutelist_content=mutelist_content)

        finding = MagicMock
        finding.check_metadata = MagicMock
        finding.check_metadata.CheckID = "check_test"
        finding.status = "FAIL"
        finding.location = "global"
        finding.resource_name = "test_resource"
        finding.tenant_domain = "test_domain"
        finding.resource_tags = []

        assert mutelist.is_finding_muted(finding, tenant_id="subscription_1")

    def test_finding_is_not_muted(self):
        # Mutelist
        mutelist_content = {
            "Accounts": {
                "subscription_1": {
                    "Checks": {
                        "check_test": {
                            "Regions": ["*"],
                            "Resources": ["test_resource"],
                        }
                    }
                }
            }
        }

        mutelist = M365Mutelist(mutelist_content=mutelist_content)

        finding = MagicMock
        finding.check_metadata = MagicMock
        finding.check_metadata.CheckID = "check_test"
        finding.status = "FAIL"
        finding.location = "global"
        finding.resource_name = "test_resource"
        finding.tenant_domain = "test_domain"
        finding.resource_tags = []

        assert not mutelist.is_finding_muted(finding, tenant_id="subscription_2")

    def test_mute_finding(self):
        # Mutelist
        mutelist_content = {
            "Accounts": {
                "subscription_1": {
                    "Checks": {
                        "check_test": {
                            "Regions": ["*"],
                            "Resources": ["test_resource"],
                        }
                    }
                }
            }
        }

        mutelist = M365Mutelist(mutelist_content=mutelist_content)

        finding_1 = generate_finding_output(
            check_id="service_check_test",
            status="FAIL",
            account_uid="subscription_1",
            region="subscription_1",
            resource_uid="test_resource",
            resource_tags=[],
            muted=False,
        )

        muted_finding = mutelist.mute_finding(finding=finding_1)

        assert muted_finding.status == "MUTED"
        assert muted_finding.muted is True
        assert muted_finding.raw["status"] == "FAIL"
