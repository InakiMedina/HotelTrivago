@wip
Feature: Client authentication

  @TC-001
  Scenario: Register with valid data
    Given I am on the client registration page
    When I register with "newuser@example.com" and "ValidPass123"
    Then my account is created
    And I can log in with "newuser@example.com" and "ValidPass123"

  @TC-002 @TC-003
  Scenario Outline: Registration is rejected
    Given I am on the client registration page
    When I register with "<email>" and "<password>"
    Then I see the error "<error>"

    Examples:
      | email                 | password                                                          | error            |
      | userexample.com       | ValidPass123                                                      | invalid email    |
      | user@                 | ValidPass123                                                      | invalid email    |
      | short-pwd@example.com | Abcde12                                                           | password length  |
      | long-pwd@example.com  | Abcdefghij1Abcdefghij1Abcdefghij1Abcdefghij1Abcdefghij1Abcdefghij | password length  |

  @TC-004
  Scenario: Register with an email that is already used
    Given I am on the client registration page
    When I register with "CLIENT1@Example.com" and "ValidPass123"
    Then I see the error "email already registered"

  @TC-005
  Scenario: Log in and log out
    Given I am logged in as "U-01"
    When I log out
    Then I am on the login page
    And my old session token is rejected

  @TC-006
  Scenario Outline: Login with invalid credentials
    Given I am on the client login page
    When I log in with "<email>" and "<password>"
    Then I see the error "Invalid email or password"

    Examples:
      | email                  | password    |
      | client1@example.com    | WrongPass1  |
      | nobody@example.com     | Client1Pass |

  @TC-007 @TC-008 @BR-06
  Scenario: A reset link works only once
    Given "U-02" requested a password reset link
    When I set the new password "NewPass2024" with that link
    Then I can log in as "U-02" with "NewPass2024"
    And the same link is rejected
