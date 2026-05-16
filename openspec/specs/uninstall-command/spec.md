## Purpose

`dm2 uninstall` CLI 命令提供统一的卸载入口，支持卸载程序包、清理项目目录、删除用户配置，所有操作前均有确认提示。

## Requirements

### Requirement: Self uninstall
The system SHALL provide `dm2 uninstall --self` that removes the DM2 tool package via pip uninstall, with confirmation prompt before execution.

#### Scenario: User confirms self uninstall
- **WHEN** user executes `dm2 uninstall --self` and confirms with "y"
- **THEN** the system SHALL execute `pip uninstall dm2-tool -y` and display success message

#### Scenario: User cancels self uninstall
- **WHEN** user executes `dm2 uninstall --self` and responds with anything other than "y"
- **THEN** the system SHALL abort the uninstall and display "已取消" message

### Requirement: Project cleanup
The system SHALL provide `dm2 uninstall --project` that removes the `.dm2/` project directory from the current working directory, with confirmation prompt listing what will be deleted.

#### Scenario: User confirms project cleanup
- **WHEN** user executes `dm2 uninstall --project` in a DM2 project directory and confirms with "y"
- **THEN** the system SHALL recursively delete `.dm2/` directory and display what was removed

#### Scenario: No project exists
- **WHEN** user executes `dm2 uninstall --project` but no `.dm2/` directory exists in current path
- **THEN** the system SHALL display "未找到 .dm2 项目" and exit

### Requirement: User config cleanup
The system SHALL provide `dm2 uninstall --user-config` that removes `~/.config/dm2/config.yaml`, with confirmation prompt showing the file path.

#### Scenario: User confirms config cleanup
- **WHEN** user executes `dm2 uninstall --user-config` and confirms with "y"
- **THEN** the system SHALL delete `~/.config/dm2/config.yaml` and display success

#### Scenario: No user config exists
- **WHEN** user executes `dm2 uninstall --user-config` but `~/.config/dm2/config.yaml` does not exist
- **THEN** the system SHALL display "未找到用户配置文件" and exit

### Requirement: No selection behavior
When `dm2 uninstall` is invoked without any option, the system SHALL display help text listing all three options.

#### Scenario: No option provided
- **WHEN** user executes `dm2 uninstall` without flags
- **THEN** the system SHALL display usage: `--self`, `--project`, `--user-config`
