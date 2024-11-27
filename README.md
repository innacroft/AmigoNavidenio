# Secret Santa Assignment Script

This script is a simple **Secret Santa assignment tool** built using Python and Flask. It allows users to submit participants' names via a web form, automatically assigns each participant a "Secret Santa," and generates unique tokens to reveal the assignments.

## Features
- **Automatic Secret Santa Assignment**: Randomly assigns a "Secret Santa" to each participant while ensuring no one is their own Santa.
- **Unique Links**: Each participant receives a unique token to view their assigned friend.
- **Persistent Storage**: Saves all assignments, tokens, and usage status in a `JSON` file for future reference.
- **Web Form Interface**: Easy-to-use form to input participants' names.
- **Secure secret**: Secret Santa's name could be seen once.
  
## Endpoints
- **add_participants**: Added participants separated by commas.
- **reveal?token=xxxxx**: Reveal secret santa by assigned on add_participants.
- **get_info**: List info by user to check url and if url has been used.
- **disable_all**: Disable all secret reveals.
- **activate_all**: Activate all secret reveals.
 
## Requirements
- Python 3.x
- Flask library

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/secret-santa
   cd secret-santa
