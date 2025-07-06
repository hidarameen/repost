# Telegram Bot Event Loop Fix

## Problem
The Telegram bot was failing with the error: **"Cannot close a running event loop"**

This error typically occurs when:
1. The bot is trying to stop while the event loop is still running
2. Signal handlers are trying to create new asyncio tasks during shutdown
3. The bot shutdown sequence is not properly coordinated

## Root Cause Analysis
The issue was in the event loop management during bot shutdown:

1. **Signal Handler Issue**: The `_signal_handler` in `main.py` was trying to create an asyncio task (`asyncio.create_task(self.stop())`) when the event loop might already be shutting down.

2. **Improper Shutdown Sequence**: The bot wasn't properly coordinating the shutdown of different components (monitoring loop, Telegram bot, etc.).

3. **Incomplete Bot Shutdown**: The `stop_bot()` method wasn't properly shutting down all components of the Telegram bot application.

## Solution

### 1. Fixed Signal Handler (`main.py`)

**Before:**
```python
def _signal_handler(self, signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    asyncio.create_task(self.stop())  # ❌ This causes the event loop error
```

**After:**
```python
def _signal_handler(self, signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    self.running = False
    # Set the shutdown event instead of creating a task
    if not self.shutdown_event.is_set():
        self.shutdown_event.set()  # ✅ Safe event-based approach
```

### 2. Improved Bot Startup/Shutdown Coordination (`main.py`)

**Before:**
```python
async def start(self):
    # ... setup code ...
    
    # Wait for tasks to complete
    await asyncio.gather(self.monitor_task, self.bot_task, return_exceptions=True)
```

**After:**
```python
async def start(self):
    # ... setup code ...
    
    # Wait for shutdown signal or task completion
    try:
        done, pending = await asyncio.wait(
            [self.monitor_task, self.bot_task, asyncio.create_task(self.shutdown_event.wait())],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel pending tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Stop the bot properly
        await self.stop()
        
    except Exception as e:
        logger.error(f"Error during bot execution: {e}")
        await self.stop()
```

### 3. Enhanced Bot Shutdown (`telegram_publisher.py`)

**Before:**
```python
async def stop_bot(self):
    """Stop the bot"""
    try:
        if self.application and self.application.running:
            await self.application.stop()  # ❌ Incomplete shutdown
            logger.info("Telegram bot stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
```

**After:**
```python
async def stop_bot(self):
    """Stop the bot"""
    try:
        if self.application and self.application.running:
            # Stop the updater first
            await self.application.updater.stop()
            # Then stop the application
            await self.application.stop()
            # Shutdown the application
            await self.application.shutdown()  # ✅ Complete shutdown sequence
            logger.info("Telegram bot stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
```

### 4. Improved Bot Initialization (`telegram_publisher.py`)

**Before:**
```python
async def run_bot(self):
    """Run the bot"""
    try:
        logger.info("Bot started successfully")
        await self.application.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        raise
```

**After:**
```python
async def run_bot(self):
    """Run the bot"""
    try:
        logger.info("Initializing Telegram bot...")
        
        # Initialize the application if not already done
        if not self.application:
            self.setup_handlers()
        
        # Initialize the application
        await self.application.initialize()  # ✅ Proper initialization
        
        logger.info("Telegram bot started successfully")
        await self.application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        raise
```

## Key Improvements

1. **Event-Based Shutdown**: Using `asyncio.Event` instead of trying to create tasks during shutdown
2. **Proper Task Cancellation**: Cancelling and waiting for tasks to complete before shutdown
3. **Complete Bot Shutdown**: Following the proper sequence: updater.stop() → application.stop() → application.shutdown()
4. **Safe Signal Handling**: Avoiding asyncio task creation in signal handlers
5. **Proper Initialization**: Ensuring the application is properly initialized before running

## Testing

You can test the fixes by running:
```bash
python3 main.py
```

The bot should now start and stop cleanly without the "Cannot close a running event loop" error.

## Summary

The event loop error was caused by improper event loop management during bot shutdown. The fixes ensure:
- Signal handlers don't try to create tasks during shutdown
- All components are properly shut down in the correct order
- Tasks are cancelled and awaited before the event loop closes
- The Telegram bot application is properly initialized and shut down

These changes should resolve the "Cannot close a running event loop" error permanently.