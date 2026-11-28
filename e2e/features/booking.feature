@wip
Feature: Booking a room type

  Background:
    Given I am logged in as "U-01"

  @BR-04
  Scenario Outline: The rooms must fit all the guests
    When I book <rooms> room(s) of "<type>" for <guests> guests
    Then the booking is <result>

    Examples:
      | type  | rooms | guests | result   |
      | R-001 | 1     | 2      | accepted |
      | R-001 | 1     | 3      | rejected |
      | R-001 | 2     | 3      | accepted |

  @BR-10
  Scenario Outline: Overbooking allows up to 110% of the physical rooms
    Given "R-001" (20 rooms, limit 22) already has <existing> reservations for TODAY+7
    When I make reservation number <new> for "R-001" from TODAY+7 to TODAY+8
    Then the booking is <result>

    Examples:
      | existing | new | result   |
      | 21       | 22  | accepted |
      | 22       | 23  | rejected |

  @BR-16 @BR-17
  Scenario Outline: Cancellation refund depends on the days left
    Given I booked "R-002" for 4 nights from <check_in> for 6000 MXN
    When I cancel the booking today
    Then I end up paying <paid> MXN

    Examples:
      | check_in | paid |
      | TODAY+2  | 0    |
      | TODAY+1  | 0    |
      | TODAY    | 3000 |

  @BR-17
  Scenario Outline: Lost and unused nights are refunded at their rate
    Given I booked "R-002" for 4 nights from TODAY for 6000 MXN
    When <event>
    Then I end up paying <paid> MXN

    Examples:
      | event                  | paid |
      | I complete the stay    | 6000 |
      | I check in 2 days late | 4500 |
      | I leave after 3 nights | 4950 |
