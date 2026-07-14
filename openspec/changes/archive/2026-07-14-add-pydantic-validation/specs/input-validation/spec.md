## ADDED Requirements

### Requirement: Student CRUD input validation

The system SHALL validate student form inputs before writing to database.

#### Scenario: Valid student creation
- **WHEN** admin fills in name (1-50 chars), no (8-12 digits), selects a class, and clicks "新增学生"
- **THEN** the data passes validation and the INSERT proceeds

#### Scenario: Invalid student number format
- **WHEN** admin enters a student number containing non-digit characters or not 8-12 digits long
- **THEN** the system SHALL display a toast error and SHALL NOT execute the INSERT

#### Scenario: Empty student name
- **WHEN** admin leaves the name field empty and clicks "新增学生"
- **THEN** the system SHALL display a toast error and SHALL NOT execute the INSERT

### Requirement: Teacher CRUD input validation

The system SHALL validate teacher form inputs before writing to database.

#### Scenario: Valid teacher creation
- **WHEN** admin fills in name (1-50 chars), no (5-20 digits), optional title and phone (7-15 digits), and clicks "新增教师"
- **THEN** the data passes validation and the INSERT proceeds

#### Scenario: Invalid phone format
- **WHEN** admin enters a phone number with non-digit characters or fewer than 7 digits
- **THEN** the system SHALL display a toast error and SHALL NOT execute the INSERT

#### Scenario: Optional fields left empty
- **WHEN** admin leaves title and phone blank
- **THEN** the system SHALL accept the submission and save NULL for those fields

### Requirement: Class CRUD input validation

The system SHALL validate class form inputs before writing to database.

#### Scenario: Valid class creation
- **WHEN** admin fills in name (1-50 chars), grade (4-digit year), major (1-100 chars), and clicks "新增班级"
- **THEN** the data passes validation and the INSERT proceeds

#### Scenario: Invalid grade format
- **WHEN** admin enters a grade that is not a 4-digit year (e.g., "23" or "2024a")
- **THEN** the system SHALL display a toast error and SHALL NOT execute the INSERT

### Requirement: Course CRUD input validation

The system SHALL validate course form inputs before writing to database.

#### Scenario: Valid course creation
- **WHEN** admin fills in name (1-100 chars), credit (1-30), and clicks "新增课程"
- **THEN** the data passes validation and the INSERT proceeds

#### Scenario: Credit out of range
- **WHEN** admin enters a credit value less than 1 or greater than 30
- **THEN** the system SHALL display a toast error and SHALL NOT execute the INSERT

### Requirement: Semester query format validation

The system SHALL validate semester query format before executing the query.

#### Scenario: Valid semester format
- **WHEN** student enters a semester in the format "2024-2025-1"
- **THEN** the system SHALL execute the semester average query

#### Scenario: Invalid semester format
- **WHEN** student enters a semester with incorrect format (e.g., "2024-25-1" or "202420251")
- **THEN** the system SHALL display a toast error and SHALL NOT execute the query
