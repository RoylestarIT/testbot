#cloud-config
package_update: true
runcmd:
  - export REVIEWPILOT_REF="${git_ref}"
  - curl -fsSL "https://raw.githubusercontent.com/RoylestarIT/testbot/$REVIEWPILOT_REF/scripts/oracle-vm-bootstrap.sh" -o /tmp/reviewpilot-bootstrap.sh
  - chmod +x /tmp/reviewpilot-bootstrap.sh
  - /tmp/reviewpilot-bootstrap.sh
