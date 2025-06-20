# 🚀 Space Shooter Game - Enhanced Edition

An epic 2D space shooter game built with Python and Pygame, featuring progressive difficulty, procedural audio, and exciting combat mechanics!

## 🎮 Game Features

### Core Gameplay
- **Progressive Level System**: 10 levels of increasing difficulty
- **Multiple Enemy Types**: Asteroids and hostile enemy ships
- **Power-up System**: Shield protection and Rapid Fire modes
- **Dynamic Scoring**: Higher level enemies give more points

### Audio & Visual Effects
- **Procedural Audio**: Background music and sound effects generated in real-time
- **Particle Systems**: Explosive visual effects
- **Scrolling Star Field**: Immersive space background
- **Level-up Animations**: Visual feedback for progression

### Advanced Features
- **Enemy AI**: Ships that move strategically and shoot at the player
- **Shield Mechanics**: Absorb one hit before taking damage
- **Rapid Fire Mode**: Temporary increased shooting speed
- **High Score Tracking**: Persistent best score tracking

## 🎯 Controls

- **Arrow Keys**: Move spaceship left/right
- **Spacebar**: Shoot bullets
- **M Key**: Toggle background music on/off
- **R Key**: Restart game (when game over)
- **Close Window**: Quit game

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Quick Start
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Game**:
   ```bash
   python space_shooter_final.py
   ```

### Alternative Setup (Virtual Environment)
```bash
# Create virtual environment
python -m venv game_env

# Activate virtual environment
# On macOS/Linux:
source game_env/bin/activate
# On Windows:
game_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python space_shooter_final.py
```

## 🎲 Gameplay Tips

### Scoring Strategy
- **Asteroids**: 10 × level points
- **Enemy Ships**: 25 × level points (higher reward!)
- **Level Up**: Every 100 points advances you one level

### Survival Tips
- Use power-ups strategically
- Shield protects from one hit - use it wisely
- Enemy ships are worth more points but are more dangerous
- Higher levels = faster enemies and more frequent spawning

### Power-ups
- **Shield** (Blue): Protects from one asteroid or enemy bullet hit
- **Rapid Fire** (Red): Increases shooting speed for limited time

## 🔧 Technical Details

### Built With
- **Python 3.x**: Core programming language
- **Pygame**: Game development framework
- **NumPy**: Audio synthesis and mathematical operations

### Architecture
- Object-oriented design with separate classes for game entities
- Real-time collision detection system
- Procedural audio generation using digital signal processing
- Event-driven game loop with 60 FPS target

## 🏆 Game Progression

| Level | Asteroid Speed | Spawn Rate | Enemy Features |
|-------|---------------|------------|----------------|
| 1-2   | Normal        | Standard   | Basic movement |
| 3-5   | +30% per level| Faster     | Increased shooting |
| 6-8   | +60% per level| Much faster| Strategic movement |
| 9-10  | Maximum speed | Rapid spawn| Elite enemies |

## 🎵 Audio Features

- **Background Music**: 4-second looping procedural melody
- **Sound Effects**: 
  - Shooting sounds (rising tone)
  - Explosion effects (noise burst with fade)
  - Power-up pickup sounds (ascending tone)
  - Level-up celebration sounds

## 🐛 Troubleshooting

### Common Issues
1. **"No module named pygame"**: Run `pip install pygame`
2. **"No module named numpy"**: Run `pip install numpy`
3. **Audio not working**: Check system audio settings
4. **Game running slowly**: Close other applications to free up resources

### Performance Tips
- Game runs best at 60 FPS
- Audio requires NumPy for procedural generation
- Close unnecessary applications for optimal performance

## 🤝 Credits

Developed collaboratively by:
- **Your Name**
- **Aditya Suyal**

Built as part of the #BuildGamesChallenge using #AmazonQDevCLI

## 📝 License

This project is open source and available under the MIT License.

## 🚀 Future Enhancements

Potential features for future versions:
- Multiplayer support
- Additional power-up types
- Boss battles
- Web deployment
- Mobile controls
- Save/load game states

---

**Enjoy the game and may the force be with you!** 🌟
