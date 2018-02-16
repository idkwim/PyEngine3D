#include "ocean_vs.glsl"

uniform sampler2D texture_diffuse;

#ifdef GL_FRAGMENT_SHADER
layout (location = 0) in VERTEX_OUTPUT vs_output;
layout (location = 0) out vec4 fs_output;

void main() {
    // vec3 texColor = texture(texture_diffuse, vs_output.tex_coord.xy).xyz;
    fs_output.xyz = vec3(1.0, 1.0, 1.0); //texColor;
    fs_output.a = 1.0;
}
#endif // GL_FRAGMENT_SHADER
