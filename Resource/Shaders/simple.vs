#version 330 core

attribute vec3 position;

layout(std140) uniform sceneConstants
{
    mat4 view;
    mat4 perspective;
    vec4 camera_position;
    vec4 light_position;
};

uniform mat4 model;

void main() {
    gl_Position = perspective * view * model * vec4(position, 1.0f);
}