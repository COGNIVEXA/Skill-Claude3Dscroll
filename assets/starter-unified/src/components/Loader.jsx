export function Loader() {
  return (
    <mesh>
      <boxGeometry args={[0.4, 0.4, 0.4]} />
      <meshBasicMaterial color="white" wireframe />
    </mesh>
  )
}
