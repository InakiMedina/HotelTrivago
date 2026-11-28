@wip
Feature: Access by role in the employee portal

  @TC-019 @BR-18
  Scenario Outline: Each role only opens its own sections
    Given I am logged in as "<user>"
    When I open the "<section>" section of the employee portal
    Then access is <result>

    Examples:
      | user | section          | result  |
      | U-01 | room management  | denied  |
      | U-03 | room management  | allowed |
      | U-04 | check-in         | allowed |
      | U-04 | room management  | denied  |
      | U-05 | housekeeping     | allowed |
      | U-05 | check-in         | denied  |
