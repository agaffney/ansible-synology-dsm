# ansible-synology-dsm

Ansible role for configuring a Synology NAS running DSM


## Overview
`ansible-synology-dsm` is an Ansible role for configuring a Synology NAS running DSM. It leverages [the Synology API](https://global.download.synology.com/download/Document/Software/DeveloperGuide/Package/FileStation/All/enu/Synology_File_Station_API_Guide.pdf) to manage various services and settings.

## Requirements
- Ansible 2.6 or higher
- Access to a Synology NAS with DSM

## Installation

### Installing Directly from GitHub Repository

1. **Create a Requirements File**:
   Create a `requirements.yml` file in your Ansible project directory with the following content:

   ```yaml
   - src: https://github.com/agaffney/ansible-synology-dsm
     name: ansible-synology-dsm
   ```

2. **Install the Role Using `ansible-galaxy`**:
   Install the role directly from the GitHub repository by running:

   ```bash
   ansible-galaxy install -r requirements.yml
   ```

3. **Reference the Role in Your Playbook**:
   Once installed, reference the role in your playbook:

   ```yaml
   - hosts: synology_nas
     roles:
       - ansible-synology-dsm
   ```

   Replace `synology_nas` with the appropriate host or group in your Ansible inventory.

This method allows you to easily incorporate the role into your Ansible workflows without needing it to be available on Ansible Galaxy.
## Usage

### Login
Establishes a session with the NAS for subsequent API requests.
```yaml
- include_tasks: login.yml
```

### Enable/Disable File Services (NFS, SMB, AFP)
```yaml
- name: Configure File Services
  hosts: synology_nas
  roles:
    - ansible-synology-dsm
  vars:
    synology_dsm_nfs_enable: true  # Enable NFS
    synology_dsm_smb_enable: true  # Enable SMB
    synology_dsm_afp_enable: false # Disable AFP
```

### Enable/Disable SSH/Telnet Services
```yaml
- name: Configure Terminal Services
  hosts: synology_nas
  roles:
    - ansible-synology-dsm
  vars:
    synology_dsm_ssh_enable: true     # Enable SSH
    synology_dsm_ssh_port: 22         # Set SSH port
    synology_dsm_telnet_enable: false # Disable Telnet
```

### Manage User Services
```yaml
- name: Configure User Services
  hosts: synology_nas
  roles:
    - ansible-synology-dsm
  vars:
    synology_dsm_user_home_service_enable: true                # Enable User Home Service
    synology_dsm_user_home_location: "/volume1/homes"          # Set home directory location
    synology_dsm_user_home_enable_recycle_bin: false           # Disable recycle bin for user homes
```

### Adding Package Sources
```yaml
- name: Add Package Sources
  hosts: synology_nas
  roles:
    - ansible-synology-dsm
  vars:
    synology_dsm_package_sources:
      - name: "Example Source"
        feed: "http://example.com/package/source"
```

## Contributing
Contributions are welcome. Please submit pull requests for any enhancements.
