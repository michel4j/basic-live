# BasicLIVE Domain Context

A framework for creating Beamline Laboratory Information Virtual Environments (LIMS) for light-source facilities.

## Language

### Identity & Organization

**Project**:
An allocated research proposal, scientific program, or billing and shipping account at the facility.
_Avoid_: Account, Client, Customer, Proposal.

**User**:
An individual human researcher, principal investigator, or facility staff member who interacts with the system.
_Avoid_: Project, Account.

**ProjectMembership**:
The formal association of a User with a Project defining their role and operational permissions.
_Avoid_: Assignment, Team Role, Project User.

**Principal Investigator**:
The researcher holding primary scientific and financial accountability for a Project and its shipments.
_Avoid_: Project Lead, Project Owner, Primary Investigator.

**Facility Account**:
A system-level Project representing the facility or a specific beamline used to own permanent hardware vessels and calibration containers.
_Avoid_: System User, Hardware Project, Admin Project.

**Proposal Portal Sync**:
The integration mechanism that synchronizes approved research proposals and team rosters from a central facility user office portal into BasicLIVE.
_Avoid_: User Importer, Portal Bridge, Sync Service.

**SSHKey**:
A public cryptographic key registered by a User or Project, used by beamline workstations to authenticate operational connections.
_Avoid_: Private Key, Host Key.

### Facility & Hardware

**Beamline**:
A physical synchrotron radiation experimental station equipped with endstation instrumentation where experiments are performed.
_Avoid_: Station, Instrument, Endstation, Hutch.

**Automounter**:
The robotic sample-changing apparatus mounted on a beamline that automatically transfers samples into the beam.
_Avoid_: Robot, Sample Changer, Carousel.

### Sample Tracking & Containment

**Shipment**:
A tracked physical consignment dispatched by a Project containing containers and samples sent to or returned from the facility.
_Avoid_: Delivery, Package, Consignment.

**Container**:
Any physical vessel with indexed locations that holds samples or sub-containers (such as shipping dewars, pucks, cassettes, or plates). Specialized beamline UI workflows may refer colloquially to pucks or plates while manipulating generic container records.
_Avoid_: Dewar, Puck, Tray, Cane.

**Sample**:
A discrete experimental specimen mounted at an indexed location within a container for beam exposure.
_Avoid_: Specimen, Crystal, Pin.

**Port**:
The composite coordinate identifier derived from the container hierarchy indicating where a sample is physically positioned for robotic mounting.
_Avoid_: Slot, Position, Coordinate, Address.

**LoadHistory**:
A chronological audit record tracking the time interval during which a child container was mounted within a parent container or automounter position.
_Avoid_: Mount Log, Transfer History, Deck History.

**Group**:
A prioritized logical batch of samples within a shipment intended to be handled or measured together.
_Avoid_: Batch, Sub-shipment, Collection.

### Scheduling & Execution

**Beamtime**:
A scheduled calendar time allocation granted to a Project on a specific Beamline.
_Avoid_: Booking, Slot, Reservation.

**Session**:
A discrete period of experimental execution conducted on a Beamline by a Project.
_Avoid_: Run, Experiment, Shift.

**Stretch**:
A continuous, uninterrupted interval of active beamline usage within a Session used to calculate active machine duration and shift consumption.
_Avoid_: Segment, Active Period, Uptime.

**Downtime**:
A recorded period during which the facility beam delivery or beamline instrumentation was unavailable for scientific operations.
_Avoid_: Outage, Maintenance Window, Shutdown.

**SupportRecord**:
An observational log entry recorded by beamline staff documenting technical assistance, problems encountered, and estimated lost operational hours.
_Avoid_: Help Ticket, Incident Log, Trouble Report.

**Remote Operator**:
An individual User designated on a Beamtime reservation authorized to remotely control beamline hardware during that shift.
_Avoid_: Driver, Remote User, Pilot.

### Experiments & Data

**Request**:
A parameterized instruction or experimental protocol attached to Samples or Groups for execution on the beamline.
_Avoid_: Job, Task, Protocol, Work Order.

**RequestType**:
A reusable specification defining the parameters, validation schema, and form layout for a Request.
_Avoid_: Protocol Type, Job Type.

**DataType**:
A category of experimental data defining expected metadata attributes and visualization templates.
_Avoid_: Experiment Type, Kind, Data Category.

**Data**:
A recorded experimental dataset collected on a beamline, comprising raw frame or scan files and associated collection metadata.
_Avoid_: Dataset, Run Output, Raw Files.

**AnalysisReport**:
The automated or manual processing results, scores, and summary reports derived from one or more Datasets.
_Avoid_: Result, Pipeline Output, Analysis.

**Download Proxy**:
An external service that authenticates and streams raw data files using temporary tokens issued by BasicLIVE.
_Avoid_: Storage Gateway, File Server, Data Broker.

### Scientific Output & Impact

**Publication**:
A formal scientific publication (such as a journal article, thesis, book, or patent) cataloged for institutional bibliometrics and impact reporting.
_Avoid_: Paper, Article, Manuscript.

**Deposition**:
A public structural or biological database entry (such as PDB, EMDB, or CSD) with an assigned accession code, resolution, and DOI resulting from facility research.
_Avoid_: Structure Entry, Protein Deposit, Database Record.
