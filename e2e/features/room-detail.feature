@wip
Feature: Room detail

  @TC-017
  Scenario: Open an existing room
    When I open the detail page of room "R-002"
    Then I see 3 photos
    And I see the amenities "Wi-Fi, Balcony"
    And I see the price "1500" per night

  @TC-017
  Scenario: Open a room that does not exist
    When I open the detail page of room "R-999"
    Then I see the message "Room not found"
