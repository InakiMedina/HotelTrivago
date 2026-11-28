@wip
Feature: Check-in and room assignment

  Background:
    Given I am logged in as "U-04"

  @BR-38
  Scenario Outline: A room is assignable only when vacant and clean
    Given room "201" is <occupancy> and <cleanliness>
    When I assign room "201" at check-in
    Then the assignment is <result>

    Examples:
      | occupancy | cleanliness        | result   |
      | occupied  | dirty              | rejected |
      | occupied  | currently cleaning | rejected |
      | vacant    | dirty              | rejected |
      | vacant    | clean              | accepted |
