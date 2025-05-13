import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, Dimensions } from 'react-native';
import Camera  from 'expo-camera';
import axios from 'axios';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

export default function App() {
  const cameraRef = useRef(null);
  const [hasPermission, setHasPermission] = useState(null);
  const [dotPos, setDotPos] = useState({ x: screenWidth / 2, y: screenHeight / 2 });
  const [action, setAction] = useState('Waiting...');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    // Reset permission state to null to ask for permissions every time the app runs
    setHasPermission(null);

    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      if (!sending) sendFrame();
    }, 1500);
    return () => clearInterval(interval);
  });

  const sendFrame = async () => {
    if (!cameraRef.current) return;
    setSending(true);
    try {
      const photo = await cameraRef.current.takePictureAsync({ base64: true, quality: 0.3 });
      const res = await axios.post('http://localhost:5071/predict', {
        image: photo.base64,
      });
      const { x, y, action } = res.data;
      setDotPos({ x: x * screenWidth, y: y * screenHeight });
      setAction(action);
    } catch (e) {
      console.log("Error:", e.message);
    }
    setSending(false);
  };

  if (hasPermission === null) return <View><Text>Requesting camera permissions...</Text></View>;
  if (hasPermission === false) return <View><Text>No access to camera</Text></View>;

  return (
    <View style={styles.container}>
      <Camera style={styles.camera} type={Camera.Constants.Type.front} />
      <View style={[styles.dot, { left: dotPos.x - 10, top: dotPos.y - 10 }]} />
      <Text style={styles.actionText}>{action}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  camera: { flex: 1 },
  dot: {
    position: 'absolute',
    width: 20,
    height: 20,
    backgroundColor: 'red',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#fff',
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
});
