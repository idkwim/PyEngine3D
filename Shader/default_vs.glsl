// input
attribute vec3 position;
attribute vec4 color;
attribute vec3 normal;
attribute vec3 bitangent;
attribute vec3 tangent;
attribute vec2 texcoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 perspective;
uniform vec3 camera_position;
uniform vec3 light_position;

// output
varying vec3 worldPosition;
varying vec4 vertexColor;
varying vec3 normalVector;
varying vec3 bitangentVector;
varying vec3 tangentVector;
varying vec2 textureCoordinate;
varying vec3 cameraVector;
varying vec3 lightVector;

void main() {
    gl_Position = perspective * view * model * vec4(position, 1.0f);
    worldPosition = position;
    vertexColor = color;
    normalVector = normal; // gl_NormalMatrix * gl_Normal;
    bitangentVector = bitangent;
    tangentVector = tangent;
    textureCoordinate = texcoord;

    cameraVector = camera_position - position;
    cameraVector = normalize(cameraVector);

    lightVector = light_position - position;
    lightVector = normalize(lightVector);
}