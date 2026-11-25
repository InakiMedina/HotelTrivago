@smoke
Feature: Backend health

  Scenario: The backend is up
    When I send GET "/health" to the backend
    Then the response status is 200
    And the response field "status" is "ok"
