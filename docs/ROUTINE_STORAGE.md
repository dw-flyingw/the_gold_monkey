# Routine Storage System

The Gold Monkey now features a persistent routine storage system that saves each custom routine in its own JSON file within the `data/routines/` folder structure.

## Overview

The routine storage system provides:
- **Individual File Storage**: Each routine stored in its own JSON file
- **Persistent Storage**: Routines survive app restarts
- **Backup & Restore**: Create and restore routine backups
- **Execution History**: Track routine performance and usage
- **Statistics**: Monitor routine usage patterns
- **File-based Storage**: Simple JSON format for easy inspection

## File Structure

```
data/routines/
├── custom_data/routines/           # Individual routine files
│   ├── tropical_sunset.json
│   ├── movie_night_setup.json
│   ├── party_mode.json
│   └── ...
├── routine_history.json       # Execution history
├── backups/                   # Backup files
│   └── backup_YYYYMMDD_HHMMSS.json
└── sample_routines.json       # Sample routines (optional)
```

## Benefits of Individual File Storage

### 1. **Better Performance**
- Load only needed routines instead of entire collection
- Faster file operations for individual routines
- Reduced memory usage for large routine collections

### 2. **Easier Management**
- Edit individual routines without affecting others
- Version control friendly (Git can track individual changes)
- Simple file operations (copy, move, delete individual routines)

### 3. **Improved Reliability**
- File corruption affects only one routine
- Easier recovery from individual file issues
- Better error isolation

### 4. **Enhanced Flexibility**
- Share individual routines between users
- Import/export specific routines
- Selective backup and restore

## Features

### 1. Custom Routines Storage
- Each routine stored in its own JSON file
- Automatic filename sanitization (spaces → underscores, special chars removed)
- File naming: `routine_name.json` (lowercase, sanitized)
- Automatic timestamp tracking (created, last run)

### 2. Execution History
- Track all routine executions with timestamps
- Record success/failure status and duration
- Store execution notes and error messages
- Automatic cleanup (keeps last 100 entries)

### 3. Backup & Restore
- Create timestamped backups of all routine data
- Restore from any previous backup
- Backup files stored in `data/routines/backups/`

### 4. Statistics & Analytics
- Total custom routines count
- Total execution count
- Success rate percentage
- Most used routine tracking
- Recent execution history
- Storage size metrics

## Usage

### In the App
1. **Custom Routines Tab**: View, run, and delete custom routines
2. **Routine Builder**: Create new custom routines
3. **Routine History Tab**: View execution history
4. **Storage & Backup Tab**: Manage backups and view statistics

### Programmatic Access
```python
from utils.routine_storage import get_routine_storage

# Get storage instance
storage = get_routine_storage()

# Load all custom routines
routines = storage.load_custom_routines()

# Get a specific routine
routine = storage.get_custom_routine("Tropical Sunset")

# Check if routine exists
exists = storage.routine_exists("Party Mode")

# Add a new routine
new_routine = {
    'name': 'My Routine',
    'description': 'A custom routine',
    'steps': [...],
    'created': '2024-01-15 10:00:00',
    'last_run': None
}
storage.add_custom_routine(new_routine)

# Update a routine
storage.update_custom_routine("My Routine", updated_routine)

# Delete a routine
storage.delete_custom_routine("My Routine")

# Get statistics
stats = storage.get_routine_stats()

# List all routine files
files = storage.list_routine_files()
```

## File Formats

### Individual Routine File Format
```json
{
  "name": "Routine Name",
  "description": "Routine description",
  "steps": [
    {
      "type": "Light Control",
      "action": "Turn On"
    },
    {
      "type": "Voice Command",
      "action": "Hello!"
    }
  ],
  "created": "2024-01-15 10:00:00",
  "last_run": "2024-01-15 15:30:00"
}
```

### Execution History Format
```json
[
  {
    "routine_name": "Routine Name",
    "timestamp": "2024-01-15 15:30:00",
    "status": "completed",
    "duration": 5.2,
    "notes": "Execution completed successfully"
  }
]
```

### Backup Format
```json
{
  "custom_routines": {
    "tropical_sunset.json": {...},
    "party_mode.json": {...}
  },
  "routine_history": [...],
  "backup_timestamp": "2024-01-15T15:30:00",
  "backup_name": "manual_backup"
}
```

## Filename Sanitization

Routine names are automatically converted to safe filenames:
- **Spaces** → `_` (underscores)
- **Special characters** → Removed
- **Case** → Lowercase
- **Multiple underscores** → Single underscore

Examples:
- `"Tropical Sunset"` → `tropical_sunset.json`
- `"Party Mode!"` → `party_mode.json`
- `"Movie Night Setup"` → `movie_night_setup.json`

## Step Types

Supported step types for routines:
- **Light Control**: Turn On, Turn Off, Set Color, Set Brightness
- **Music Control**: Play, Pause, Next, Previous
- **TV Control**: Power On, Power Off, Home, Launch App
- **Voice Command**: Text-to-speech messages
- **Wait**: Pause execution for specified seconds

## Management

### Creating Backups
1. Go to Routines → Storage & Backup tab
2. Enter optional backup name
3. Click "Create Backup"
4. Backup saved to `data/routines/backups/`

### Restoring Backups
1. Go to Routines → Storage & Backup tab
2. Select backup file from dropdown
3. Click "Restore Backup"
4. All routine data restored from backup

### Manual File Editing
- Individual routines: Edit files in `data/routines/custom_data/routines/`
- History: Edit `data/routines/routine_history.json`
- Backup files: Edit any file in `data/routines/backups/`

### File Operations
```bash
# Copy a routine to share
cp data/routines/custom_data/routines/tropical_sunset.json shared_data/routines/

# Rename a routine file
mv data/routines/custom_data/routines/old_name.json data/routines/custom_data/routines/new_name.json

# Delete a routine
rm data/routines/custom_data/routines/unwanted_routine.json
```

## Error Handling

The storage system includes comprehensive error handling:
- File I/O errors logged with details
- Graceful fallback to empty data on corruption
- Automatic directory creation
- JSON validation and error recovery
- Individual file error isolation

## Performance

- **Fast Loading**: Only load needed routines
- **Efficient Updates**: Update only modified files
- **History Management**: Automatic cleanup prevents file bloat
- **Backup Optimization**: Compressed backup format
- **Memory Efficient**: No need to load entire routine collection

## Security

- **Local Storage**: All data stored locally on device
- **No Network**: No external data transmission
- **File Permissions**: Respects system file permissions
- **Backup Encryption**: Consider encrypting sensitive backups
- **Filename Sanitization**: Prevents path traversal attacks

## Troubleshooting

### Common Issues

1. **Routines Not Loading**
   - Check file permissions on `data/routines/custom_data/routines/` folder
   - Verify JSON syntax in individual routine files
   - Check app logs for error messages

2. **Backup/Restore Fails**
   - Ensure sufficient disk space
   - Check file permissions on backup directory
   - Verify backup file integrity

3. **Performance Issues**
   - Large number of routine files may slow directory listing
   - Consider organizing routines into subdirectories
   - Check disk space availability

4. **Filename Issues**
   - Check filename sanitization for special characters
   - Ensure routine names are unique
   - Verify file naming conventions

### Debug Commands

```bash
# Test storage system
python utils/test_routine_storage.py

# Migrate from old storage (if needed)
python utils/migrate_routine_storage.py

# Load sample routines
python utils/load_sample_routines.py

# Check file structure
ls -la data/routines/custom_data/routines/

# Validate JSON syntax
python -m json.tool data/routines/custom_data/routines/tropical_sunset.json

# Count routine files
find data/routines/custom_data/routines/ -name "*.json" | wc -l
```

## Migration

If you have existing routines in the old single-file format, use the migration script:

```bash
python utils/migrate_routine_storage.py
```

This will:
1. Create a backup of the old file
2. Convert each routine to individual files
3. Remove the old single file
4. Verify the migration

## Future Enhancements

Potential improvements:
- **Database Storage**: SQLite for better performance with large collections
- **Cloud Sync**: Backup to cloud storage
- **Routine Sharing**: Export/import individual routine files
- **Advanced Analytics**: Usage patterns and optimization
- **Scheduled Routines**: Time-based automation
- **Routine Templates**: Pre-built routine categories
- **Subdirectories**: Organize routines by category
- **Routine Versioning**: Track changes to individual routines 