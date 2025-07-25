from prowler.config.config import timestamp
from prowler.lib.check.compliance_models import Compliance
from prowler.lib.outputs.compliance.compliance_output import ComplianceOutput
from prowler.lib.outputs.compliance.iso27001.models import KubernetesISO27001Model
from prowler.lib.outputs.finding import Finding


class KubernetesISO27001(ComplianceOutput):
    """
    This class represents the Kubernetes ISO 27001 compliance output.

    Attributes:
        - _data (list): A list to store transformed data from findings.
        - _file_descriptor (TextIOWrapper): A file descriptor to write data to a file.

    Methods:
        - transform: Transforms findings into Kubernetes ISO 27001 compliance format.
    """

    def transform(
        self,
        findings: list[Finding],
        compliance: Compliance,
        compliance_name: str,
    ) -> None:
        """
        Transforms a list of findings into Kubernetes ISO 27001 compliance format.

        Parameters:
            - findings (list): A list of findings.
            - compliance (Compliance): A compliance model.
            - compliance_name (str): The name of the compliance model.

        Returns:
            - None
        """
        for finding in findings:
            # Get the compliance requirements for the finding
            finding_requirements = finding.compliance.get(compliance_name, [])
            for requirement in compliance.Requirements:
                if requirement.Id in finding_requirements:
                    for attribute in requirement.Attributes:
                        compliance_row = KubernetesISO27001Model(
                            Provider=finding.provider,
                            Description=compliance.Description,
                            Context=finding.account_name,
                            Namespace=finding.region,
                            AssessmentDate=str(timestamp),
                            Requirements_Id=requirement.Id,
                            Requirements_Description=requirement.Description,
                            Requirements_Name=requirement.Name,
                            Requirements_Attributes_Category=attribute.Category,
                            Requirements_Attributes_Objetive_ID=attribute.Objetive_ID,
                            Requirements_Attributes_Objetive_Name=attribute.Objetive_Name,
                            Requirements_Attributes_Check_Summary=attribute.Check_Summary,
                            Status=finding.status,
                            StatusExtended=finding.status_extended,
                            ResourceId=finding.resource_uid,
                            CheckId=finding.check_id,
                            Muted=finding.muted,
                            ResourceName=finding.resource_name,
                        )
                        self._data.append(compliance_row)
        # Add manual requirements to the compliance output
        for requirement in compliance.Requirements:
            if not requirement.Checks:
                for attribute in requirement.Attributes:
                    compliance_row = KubernetesISO27001Model(
                        Provider=compliance.Provider.lower(),
                        Description=compliance.Description,
                        Context="",
                        Namespace="",
                        AssessmentDate=str(timestamp),
                        Requirements_Id=requirement.Id,
                        Requirements_Description=requirement.Description,
                        Requirements_Name=requirement.Name,
                        Requirements_Attributes_Category=attribute.Category,
                        Requirements_Attributes_Objetive_ID=attribute.Objetive_ID,
                        Requirements_Attributes_Objetive_Name=attribute.Objetive_Name,
                        Requirements_Attributes_Check_Summary=attribute.Check_Summary,
                        Status="MANUAL",
                        StatusExtended="Manual check",
                        ResourceId="manual_check",
                        ResourceName="Manual check",
                        CheckId="manual",
                        Muted=False,
                    )
                    self._data.append(compliance_row)
