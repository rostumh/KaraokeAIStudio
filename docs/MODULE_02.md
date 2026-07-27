# Module 2 — Modern Desktop UI

## Scope

Module 2 replaces the initial shell with a production-grade PySide6 workspace. It implements the application frame, menu system, toolbar, accessible sidebar navigation, dockable project and properties panels, studio preview, waveform/timeline presentation, lyrics editor shell, batch queue, history, settings interface, persistent window layout, status reporting, keyboard shortcuts, and an MVVM presentation-state layer.

No media is decoded in this module. The Import dialog validates supported file selection and hands the selected path to the future Module 3 ingestion workflow. This is a deliberate architecture boundary, not missing UI implementation.

## UI architecture

- `MainWindow` composes the desktop shell and owns process-level Qt actions.
- `WorkspaceViewModel` owns navigation, playback, and normalized seek presentation state.
- Views provide page-specific composition without application or infrastructure dependencies.
- Widgets encapsulate reusable controls such as navigation, preview, waveform, timeline, and dock contents.
- Native `QSettings` stores only window geometry and dock layout. Product configuration remains JSON-based.
- Standard Qt icons are DPI-aware and avoid fragile filesystem paths. Custom branded artwork can be added later through Qt resources.

## Accessibility and interaction

All core actions have labels, tooltips, or accessible names. Navigation buttons are keyboard focusable. Standard shortcuts include Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+E, Space, and the platform quit shortcut. Layout state restores across runs and can be reset from the View menu.

## Performance

The workspace constructs lightweight widgets only. There are no timers, background loops, or eager media/model loads. Waveform drawing uses a single antialiased painter path and will be replaced with cached decoded peaks when Module 3 introduces real media state.

## Run and test

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python main.py
python -m pytest
python -m ruff check .
python -m mypy app
```

## Expected output

The application opens at 1440×900 with sidebar navigation, a movable toolbar, Project and Properties docks, Studio preview, transport controls, waveform overview, and a persistent status bar. All five workspace pages are available. Window size and dock positions restore after restart.

## Acceptance criteria

- All five pages navigate without rebuilding the application.
- Docks can move, hide, and restore.
- Window geometry and dock state survive restart.
- Toolbar, menu actions, and keyboard shortcuts remain synchronized.
- Playback presentation state toggles and resets through the view model.
- Import accepts every format specified for the product and cancels safely.
- UI startup and view-model tests pass using Qt's offscreen backend.
