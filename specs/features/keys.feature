Feature: Client API Keys Management
  As a developer using 9Router
  I want to create, list, and revoke API keys via CLI
  So that I can configure local coding agents

  Scenario: Creating and revoking an API key
    Given 9router server is running on localhost:20128
    When I run "9r keys create test-cli-agent --json"
    Then the exit code should be 0
    And the response contains a key starting with "sk-"
    When I run "9r keys delete <key_id> --yes"
    Then the exit code should be 0
