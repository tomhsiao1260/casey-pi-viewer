import { ShaderMaterial, Vector2, AdditiveBlending, DoubleSide } from "three";

export class ParticleMaterial extends ShaderMaterial {
  constructor(params) {
    super({
      depthWrite: false,
      vertexColors: true,
      side: DoubleSide,
      blending: AdditiveBlending,

      uniforms: {
        uTexture : { value: null },
        uSize: { value: 5.0 },
      },

      vertexShader: /* glsl */ `
        varying vec2 vUv;
        uniform float uSize;

        void main() {
          vUv = uv;
          vec3 newPosition = position;

          vec4 modelPosition = modelMatrix * vec4(newPosition, 1.0);
          vec4 viewPosition = viewMatrix * modelPosition;
          vec4 projectedPosition = projectionMatrix * viewPosition;

          gl_Position = projectedPosition;

          gl_PointSize = uSize;
          gl_PointSize *= (1.0 / - viewPosition.z);
      }
      `,

      fragmentShader: /* glsl */ `
        uniform sampler2D uTexture;
        varying vec2 vUv;

        void main()
        {
            vec3 color = vec3(vUv, 1.0);

            // gl_FragColor  = texture2D(uTexture, vec2(0.5));
            gl_FragColor  = texture2D(uTexture, gl_PointCoord);
            gl_FragColor *= vec4(color, 1.0);
        }
      `
    });

    this.setValues(params);
  }
}
