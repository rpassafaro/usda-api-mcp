# GUI Installer for USDA Food Tools

Beautiful, user-friendly graphical installers for Mac and Windows users who prefer point-and-click installation.

## 🖱️ Mac GUI Installer

### For End Users

**Two Easy Options:**

#### Option A: Native Mac App (Recommended)
1. Download: [`USDA Food Tools Installer.zip`](dist/USDA%20Food%20Tools%20Installer.zip)
2. Extract the zip file
3. Double-click `USDA Food Tools Installer.app`
4. Follow the beautiful interface
5. Enter your USDA API key when prompted
6. Click "Install" and restart Claude

#### Option B: Python Script
1. Download: [`gui_installer.py`](gui_installer.py) 
2. Double-click to run (requires Python 3.11+)
3. Follow the on-screen instructions
4. Enter your USDA API key when prompted
5. Click "Install" and restart Claude

**What the GUI Does:**
- ✅ **System Check** - Verifies Claude for Desktop and Python
- ✅ **API Key Validation** - Tests your key with USDA API
- ✅ **Automatic Installation** - Installs everything without Terminal
- ✅ **Progress Tracking** - Shows real-time installation progress
- ✅ **Error Handling** - Clear error messages and solutions
- ✅ **Claude Integration** - Automatically configures Claude for Desktop

### Creating a Mac App Bundle

**For Developers - Build a native .app:**

1. **Install dependencies:**
   ```bash
   pip3 install py2app requests
   ```

2. **Build the app:**
   ```bash
   ./build_installer.sh
   ```
   
   Or manually:
   ```bash
   python3 setup_gui.py py2app
   ```

3. **Create distribution package:**
   ```bash
   cd dist
   zip -r "USDA Food Tools Installer.zip" "USDA Food Tools Installer.app"
   ```

**What users get:**
- Download the .zip file  
- Extract and double-click the `.app`
- Native Mac application with beautiful interface
- No Python knowledge needed!
- Code-signed and ready for distribution

## 🪟 Windows GUI Installer

### Current Status
The Windows GUI installer (`windows_installer.py`) is **ready but limited**:
- ✅ Beautiful Windows-style interface
- ✅ System prerequisite checking
- ⚠️ Installation flow needs Windows-specific implementation

### For Windows Users (Current Options)
1. **WSL/Git Bash**: Use the `install.sh` script
2. **Command Line**: Use `pip` and manual configuration
3. **Wait**: Full Windows .exe installer coming soon!

### Future Windows .exe Installer
Planning to create with:
- **PyInstaller** or **cx_Freeze** for .exe creation
- **Inno Setup** for professional Windows installer
- **Auto-updater** for future versions
- **Windows Registry** integration

## 📋 GUI Features

### Mac GUI (`gui_installer.py` & Mac App)
- 🎨 **Native Mac styling** with SF Pro fonts
- 🔍 **System verification** - Checks Claude and Python automatically
- 🌐 **Integrated browser** - Opens API key registration page
- 📊 **Progress tracking** - Real-time installation updates with progress bar
- ✅ **API key validation** - Tests key with USDA API before proceeding
- 🔄 **Auto-restart** - Offers to restart Claude automatically when done
- 💾 **Safe installation** - Backs up existing configurations safely
- 🔐 **Error handling** - Clear, helpful error messages with solutions
- 📱 **User-friendly** - No Terminal or technical knowledge required

### Windows GUI (`windows_installer.py`) 
- 🎨 **Windows 11 styling** with Segoe UI fonts
- 🔍 **Multi-location checking** - Finds Claude in various install locations
- 📱 **Cross-platform ready** - Prepared for full Windows implementation
- 🛡️ **Error handling** - Windows-specific error messages

## 🛠️ Development Guide

### Adding GUI Features

**For Mac installer:**
```python
# Add new installation step
def _new_installation_step(self):
    self.root.after(0, lambda: self.update_progress(45, "Doing new thing..."))
    # Implementation here
    
# Add to _install_bg method:
self._new_installation_step()
```

**For Windows installer:**
```python
# Windows-specific implementation
if sys.platform == "win32":
    # Windows-specific code
    pass
```

### GUI Testing

**Mac testing:**
```bash
# Test GUI directly
python3 gui_installer.py

# Test app bundle
./build_installer.sh
open dist/gui_installer.app
```

**Windows testing:**
```bash
# Test on Windows (future)
python windows_installer.py
```

### Customization Options

- **Colors**: Modify `primary_color`, `success_color`, etc.
- **Fonts**: Change font families for different platforms
- **Layout**: Adjust widget positioning and sizing
- **Features**: Add validation, progress steps, or integrations

## 📦 Distribution

### Mac Distribution
1. **Direct Python**: Share `gui_installer.py` 
2. **App Bundle**: Share `gui_installer.app.zip`
3. **DMG**: Create disk image for professional distribution

### Windows Distribution (Future)
1. **Python Script**: Share `windows_installer.py`
2. **Executable**: Create `.exe` with PyInstaller
3. **MSI Installer**: Professional Windows installer package

## 🎯 User Experience Goals

### Non-Technical Users
- ✅ **No Terminal required** for Mac users
- ✅ **Visual progress feedback** during installation
- ✅ **Clear error messages** with solutions
- ✅ **One-click installation** after entering API key
- ✅ **Automatic Claude configuration**

### Power Users  
- ✅ **Command-line option** still available (`install.sh`)
- ✅ **Developer documentation** for customization
- ✅ **Source code access** for modification
- ✅ **Build scripts** for creating distributions

## 🚀 Future Enhancements

### Planned Features
- 🔄 **Auto-updater** - Check for new versions
- 🌙 **Dark mode support** - Follow system preferences  
- 🌍 **Internationalization** - Multi-language support
- 📊 **Usage analytics** - Anonymous usage statistics
- 🔐 **Keychain integration** - Secure API key storage (Mac)
- 🪟 **Native Windows installer** - Professional .msi package

### Advanced Features
- 📱 **Mobile-responsive** - Tablet-friendly interface
- 🎛️ **Advanced configuration** - Custom installation options
- 🔌 **Plugin system** - Additional tool integrations
- 📈 **Health monitoring** - Check tool status and performance

The GUI installers make the USDA Food Tools accessible to everyone, regardless of technical expertise! 🎉
