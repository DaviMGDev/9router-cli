Feature: Combos Management
  As a developer using 9Router
  I want to create, list, inspect, and delete model combos from the CLI
  So that I can automate fallback routing without breaking the WebUI

  Scenario: Listing combos
    Given 9router server is running on localhost:20128
    When I run "9r combos list --json"
    Then the exit code should be 0
    And the output should be a JSON array of combos

  Scenario: Creating a combo with string model IDs
    Given 9router server is running on localhost:20128
    When I run "9r combos create cli-test-combo --model ag/gemini-3.8-flash --model ag/gemini-3.8-flash-low"
    Then the exit code should be 0
    And the combo "cli-test-combo" should exist with 2 string models

  Scenario: Deleting a combo
    Given combo "cli-test-combo" exists
    When I run "9r combos delete cli-test-combo --yes"
    Then the exit code should be 0
    And the combo "cli-test-combo" should not exist
