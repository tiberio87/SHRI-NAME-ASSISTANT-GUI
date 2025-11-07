# Changelog - SHRI MKV Rename Assistant

## [v1.0.0] - 2025-11-06

### 🎉 Initial Release
- ✅ Complete GUI application for MKV file renaming
- ✅ Scene naming compliance (ENCODE/WEB-DL/REMUX)
- ✅ MediaInfo integration for metadata extraction
- ✅ Comprehensive test suite with 100% pass rate

### 🔧 Core Features
- **File Selection**: GUI file picker with preview
- **MediaInfo Display**: Complete file information display
- **Scene Naming**: Automatic scene-compliant name generation
- **Resolution Detection**: Accurate resolution classification
- **HDR/DV Support**: Full HDR and Dolby Vision detection
- **Audio Detection**: Multi-track audio format detection
- **Service Detection**: Streaming service identification

### 🐛 Major Fixes Implemented
- **Resolution Fix**: 1920x804 correctly classified as 1080p (not 720p)
- **ENCODE/REMUX Fix**: Proper detection using Writing Library metadata
- **HDR Detection Fix**: Complete HDR/DV extraction from MediaInfo fields

### 📋 Technical Specifications
- **Python**: 3.12+ compatibility
- **GUI Framework**: tkinter (native Python GUI)
- **Media Library**: pymediainfo for metadata extraction
- **Platform**: Windows optimized (batch launcher included)

### 🧪 Test Coverage
- `test_mkv_assistant.py`: General application tests
- `test_resolution_fix.py`: Resolution classification validation
- `test_encode_remux_fix.py`: ENCODE/REMUX detection tests
- `test_hdr_fix.py`: HDR/Dolby Vision detection tests
- `test_scene_patterns.py`: Scene naming pattern validation

### 📁 Files Structure
```
mkv_rename_assistant.py    # Main GUI application
config.py                  # Configuration and mappings
start_mkv_assistant.bat    # Windows launcher
test_*.py                  # Comprehensive test suite
README_MKV_ASSISTANT.md    # User documentation
ESEMPI_TEST.md            # Test examples and cases
```

### 🎯 Scene Rules Compliance
- ✅ **ENCODE**: x264/x265 encoded releases
- ✅ **WEB-DL**: Direct streaming downloads  
- ✅ **REMUX**: Lossless BluRay remuxes
- ✅ **Resolution**: 480p/720p/1080p/2160p classification
- ✅ **HDR**: HDR10/DV/HDR10+/HLG support
- ✅ **Audio**: DTS/AC3/AAC/FLAC detection
- ✅ **Services**: Netflix/Amazon/Disney+/etc identification

---

## Future Versions

### [v1.1.0] - Planned
- [ ] Batch processing for multiple files
- [ ] Drag & drop file interface
- [ ] Undo/Redo functionality
- [ ] Preview mode before renaming

### [v1.2.0] - Planned  
- [ ] Custom naming rules
- [ ] Dark theme support
- [ ] Configuration GUI
- [ ] Recent files history

### [v2.0.0] - Future
- [ ] Plugin system architecture
- [ ] API integrations (TMDb, etc.)
- [ ] Advanced metadata detection
- [ ] Cross-platform GUI (Qt/GTK)

---

**Current Status**: ✅ Production Ready  
**Next Release**: TBD  
**Branch**: `master` (stable) / `dev` (development)