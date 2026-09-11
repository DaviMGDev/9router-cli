Feature: Providers and Models Inspection
  As a developer using 9Router
  I want to list connected providers and discover available models
  So that I know what models can be routed

  Scenario: Listing active providers
    Given 9router server is running on localhost:20128
    When I run "9r providers list --json"
    Then the exit code should be 0
    And the output contains active provider connections

  Scenario: Listing available models
    Given 9router server is running on localhost:20128
    When I run "9r models list --json"
    Then the exit code should be 0
    And each model in the list has an id and owner
