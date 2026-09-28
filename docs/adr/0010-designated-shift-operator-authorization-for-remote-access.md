# Designated Shift Operator Authorization for Remote Access

Remote beamline operation introduces critical safety, radiation control, and cybersecurity requirements during active beam delivery. We decided that remote workstation access managed by the ACL module is granted exclusively to specific individual `User` accounts explicitly designated as "Remote Operators" on the scheduled `Beamtime` reservation, rather than granting blanket network access to an entire research project team.

## Amendment (Decoupled User and Project Architecture)

With the decoupling of individual human `User` accounts from research allocation `Project` models (see issue #120 / #124):
- Workstation access authorization managed by the ACL module is configured at the **Project** level:
  - **Manual Access**: `AccessList.users` maintains a `ManyToManyField` to `Project`. Manually assigning a `Project` authorizes all members of that project.
  - **Scheduled Access**: During active remote `Beamtime` shifts, all members of the scheduled `Project` (the PI and all users registered in `project.members` through `ProjectMembership`) are authorized for remote workstation login.
- **Individual Credential Authentication**: Workstations authenticate individual connecting users via their personal registered `SSHKey` credentials on `lims.User`. This supersedes the previous single-operator restriction while ensuring personal auditability and accountability.
