import { useRef, useState, useEffect } from 'react';
import { View, Text, StyleSheet, Dimensions, Button, TouchableOpacity } from 'react-native';
import { CameraView, useCameraPermissions, CameraType } from 'expo-camera';
import io from 'socket.io-client';

const socket = io('https://9e6b-14-139-98-164.ngrok-free.app', { transports: ['websocket'] }); // Replace <your-server-ip> with your Flask server's IP
const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

export default function App() {
  const cameraRef = useRef(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [dotPos, setDotPos] = useState({ x: screenWidth / 2, y: screenHeight / 2 });
  const [targetPos, setTargetPos] = useState({ x: screenWidth / 2, y: screenHeight / 2 });
  const [action, setAction] = useState('Waiting...');
  const [sending, setSending] = useState(false);
  const [buttonPressCount, setButtonPressCount] = useState(0); // State to track button presses
  const [countdown, setCountdown] = useState(null); // Countdown timer state
  const [isFocused, setIsFocused] = useState(false); // Whether the dot is focused on the button
  const CameraType = {
    front: 'front',
    back: 'back',
  };

  const [facing, setFacing] = useState(CameraType.front);

  useEffect(() => {
    if (!permission || !permission.granted) {
      requestPermission();
    }
  }, [permission]);

  useEffect(() => {
    socket.on('connect', () => {
      console.log('Connected to Flask-SocketIO server');
    });

    socket.on('response', (data) => {
      console.log('Response from server:', data);
      const { x, y, action } = data;
      setTargetPos({ x: x * screenWidth, y: y * screenHeight }); // Update target position
      setAction(action);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      if (!sending) sendFrame();
    }, 1000);
    return () => clearInterval(interval);
  }, [sending]);

  // Smoothly move the dot toward the target position
  useEffect(() => {
    const animationInterval = setInterval(() => {
      setDotPos((currentPos) => {
        const dx = targetPos.x - currentPos.x;
        const dy = targetPos.y - currentPos.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // If the dot is close enough to the target, stop moving
        if (distance < 1) {
          return targetPos;
        }

        // Move the dot a small step toward the target
        const step = 10; // Adjust step size for speed
        const angle = Math.atan2(dy, dx);
        return {
          x: currentPos.x + step * Math.cos(angle),
          y: currentPos.y + step * Math.sin(angle),
        };
      });
    }, 16); // Run at ~60 FPS

    return () => clearInterval(animationInterval);
  }, [targetPos]);

  // Check if the dot is within the button's region
  useEffect(() => {
    const buttonX = screenWidth / 2 - 75; // Button's left boundary
    const buttonY = screenHeight - 500; // Button's top boundary
    const buttonWidth = 150;
    const buttonHeight = 50;

    if (
      dotPos.x >= buttonX &&
      dotPos.x <= buttonX + buttonWidth &&
      dotPos.y >= buttonY &&
      dotPos.y <= buttonY + buttonHeight
    ) {
      if (!isFocused) {
        setIsFocused(true);
        setCountdown(3.0); // Start countdown
      }
    } else {
      setIsFocused(false);
      setCountdown(null); // Reset countdown if the dot moves away
    }
  }, [dotPos]);

  // Handle countdown logic
  useEffect(() => {
    if (isFocused && countdown !== null) {
      const countdownInterval = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 0) {
            clearInterval(countdownInterval);
            setButtonPressCount((prevCount) => prevCount + 1); // Simulate button press
            setIsFocused(false); // Reset focus
            return null; // Stop countdown
          }
          return (prev - 0.1).toFixed(2); // Decrease countdown by 0.1 seconds
        });
      }, 100);

      return () => clearInterval(countdownInterval);
    }
  }, [isFocused, countdown]);

  const sendFrame = async () => {
    if (!cameraRef.current) return;
    setSending(true);
    try {
      const photo = await cameraRef.current.takePictureAsync({ base64: true, quality: 0.1 });
      console.log('Sending frame to server...');
      socket.emit('process_frame', { image: photo.base64 });
    } catch (e) {
      console.log('Error:', e.message);
    }
    setSending(false);
  };

  if (!permission) return <View />;
  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.message}>We need camera permission to continue.</Text>
        <Button title="Grant Permission" onPress={requestPermission} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <CameraView
        ref={cameraRef}
        style={styles.camera}
        facing={facing}
        enableZoomGesture={false}
        photo={true}
      />
      <View style={[styles.dot, { left: dotPos.x - 1, top: dotPos.y - 1 }]} />
      <Text style={styles.actionText}>{action}</Text>

      {/* Button to track presses */}
      <TouchableOpacity
        style={styles.pressButton}
        onPress={() => setButtonPressCount((prevCount) => prevCount + 1)}
      >
        <Text style={styles.pressButtonText}>Pressed {buttonPressCount} times</Text>
      </TouchableOpacity>

      {/* Countdown Timer */}
      {isFocused && countdown !== null && (
        <Text style={styles.countdownText}>{countdown}s</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  message: {
    textAlign: 'center',
    marginTop: 40,
    fontSize: 16,
  },
  camera: {
    flex: 1,
  },
  dot: {
    position: 'absolute',
    width: 10,
    height: 10,
    backgroundColor: 'red',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#fff',
    zIndex: 10,
  },
  actionText: {
    position: 'absolute',
    bottom: 30,
    left: 20,
    fontSize: 18,
    color: '#fff',
    backgroundColor: 'rgba(0,0,0,0.5)',
    padding: 6,
    borderRadius: 5,
  },
  pressButton: {
    position: 'absolute',
    bottom: 500,
    left: '50%',
    transform: [{ translateX: -75 }],
    width: 150,
    height: 50,
    backgroundColor: '#007BFF',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 10,
    opacity: 0.4,
  },
  pressButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  countdownText: {
    position: 'absolute',
    bottom: 550,
    left: '50%',
    transform: [{ translateX: -50 }],
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FF0000',
  },
});
