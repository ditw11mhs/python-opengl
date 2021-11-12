import streamlit as st
import streamlit.components.v1 as components
from backend_opengl import *


class Main:
    def main(self):
    
        st.markdown("# 3D Motion")
        c1,c2 = st.columns(2)
        camera_radius = c1.slider("Camera Radius", 0, 500,135)
        camera_theta = c1.slider("Camera Theta", 0, 360,77)
        camera_phi = c1.slider("Camera Phi", 0, 360,44)
        # x_1&=l_{1p}sin{\theta_1}cos{\varphi_1}\\
        #             y_1&=l_{1p}sin{\theta_1}sin{\varphi_1}\\
        #             z_1 &= -l_{1p}cos{\theta_1}\\
        H = c2.number_input("Height", 0, 220,160)
        l1 =  0.186 * H
        l2 = 0.146 * H
        
        components.html(
            f"""
            <canvas id="canvas" width = "640" height = "640"></canvas>
         
            
            <script src="https://twgljs.org/dist/3.x/twgl-full.min.js"></script>
            
            <script>
            const m4 = twgl.m4;
            const v3 = twgl.v3;
            const gl = document.querySelector("canvas").getContext("webgl");

            const vs = `
            attribute vec4 position;
            attribute vec3 normal;

            uniform mat4 u_projection;
            uniform mat4 u_view;
            uniform mat4 u_model;

            varying vec3 v_normal;

            void main() {{
            gl_Position = u_projection * u_view * u_model * position;
            v_normal = mat3(u_model) * normal; // better to use inverse-transpose-model
            }}
            `

            const fs = `
            precision mediump float;

            varying vec3 v_normal;

            uniform vec3 u_lightDir;
            uniform vec3 u_color;

            void main() {{
            float light = dot(normalize(v_normal), u_lightDir) * .5 + .5;
            gl_FragColor = vec4(u_color * light, 1);
            }}
            `;

            // compiles shaders, links program, looks up attributes
            const programInfo = twgl.createProgramInfo(gl, [vs, fs]);
            // calls gl.createBuffer, gl.bindBuffer, gl.bufferData
            
            sphereRad =3;
            
            const cubeBufferInfo = twgl.primitives.createCubeBufferInfo(gl, 1);
            const sphereBufferInfo = twgl.primitives.createSphereBufferInfo(gl,sphereRad,200,200);
            const cylinderBufferInfo = twgl.primitives.createCylinderBufferInfo(gl,sphereRad/2,{l1}+2*sphereRad,200,200);
            const truncatCylinderBufferInfo = twgl.primitives.createTruncatedConeBufferInfo(gl,sphereRad/3,sphereRad/2,{l2}+2*sphereRad,200,200); 
            
            r = {camera_radius};
            theta_camera = {camera_theta}*Math.PI/180;
            phi = {camera_phi}*Math.PI/180;
            
            x = r*Math.sin(theta_camera)*Math.cos(phi);
            z = r*Math.sin(theta_camera)*Math.sin(phi);
            y = -r*Math.cos(theta_camera);
            
            
            const stack = [];

            const color = [1, 1,1];
            const lightDir = v3.normalize([x, y, z]);
            
            function render(time) {{
            time *= 0.001;
            
            
            console.log(theta_camera);
            f_shoulder = 0.25;
            
            rotate_shoulder_x = 2*Math.abs(Math.sin(2*Math.PI*f_shoulder*time));
            rotate_shoulder_y = 1*Math.abs(Math.sin(2*Math.PI*f_shoulder*time));
            
            twgl.resizeCanvasToDisplaySize(gl.canvas);
            gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);
            
            gl.enable(gl.DEPTH_TEST);
            gl.enable(gl.CULL_FACE);
            
            gl.useProgram(programInfo.program);
            
            const fov = Math.PI * .25;
            const aspect = gl.canvas.clientWidth / gl.canvas.clientHeight;
            const zNear = 0.01;
            const zFar = 1000;
            const projection = m4.perspective(fov, aspect, zNear, zFar);
            
            const cameraPosition = [x, y, z];
            const target = [0, -10, 0];
            const up = [0, 1, 0];
            const camera = m4.lookAt(cameraPosition, target, up);
            
            const view = m4.inverse(camera);
            
            
            // make base position for shoulder
            let m = m4.translation([0, 0, 0]);
            pushMatrix(m);
            {{
                //Shoulder Sphere
                m = m4.rotateX(m, rotate_shoulder_x);
                m = m4.rotateY(m, rotate_shoulder_y);
                drawSphere(projection, view, m);
                pushMatrix(m);
                {{
                    // Upper Arm
                    m = m4.translate(m, [0, -({l1}/2+sphereRad), 0]);
                    drawCylinder(projection, view, m);
                    
                    pushMatrix(m);
                    {{
                    // Elbow
                    m = m4.translate(m, [0, -({l1/2}+sphereRad), 0]);
                    m = m4.rotateX(m, rotate_shoulder_y);
                    
                    drawSphere(projection, view, m);
                    pushMatrix(m);
                    {{
                        // Lower Arm
                        m = m4.translate(m, [0, -({l2/2}+sphereRad), 0]);
                        drawCone(projection, view, m);
                        pushMatrix(m);
                        {{
                            //Hand
                            m = m4.translate(m, [0, -({l2/2}+sphereRad), 0]);
                            drawSphere(projection, view, m);
                            pushMatrix(m);
                        }}
                    }}
                    }}
                    
                }}
            
                
            
                
            }}
            
            m = popMatrix();

            requestAnimationFrame(render);
            }}
            requestAnimationFrame(render);

            function pushMatrix(m) {{
            stack.push(m);
            }}

            function popMatrix() {{
            return stack.pop();
            }}

            function drawCube(projection, view, model) {{
            twgl.setBuffersAndAttributes(gl, programInfo, cubeBufferInfo);
            twgl.setUniforms(programInfo, {{
                u_color: color,
                u_lightDir: lightDir,
                u_projection: projection,
                u_view: view,
                u_model: model,
            }});
            
            twgl.drawBufferInfo(gl, cubeBufferInfo);
            }}
            
            function drawSphere(projection, view, model) {{
            twgl.setBuffersAndAttributes(gl, programInfo, sphereBufferInfo);
        
            twgl.setUniforms(programInfo, {{
                u_color: color,
                u_lightDir: lightDir,
                u_projection: projection,
                u_view: view,
                u_model: model,
            }});
          
            twgl.drawBufferInfo(gl, sphereBufferInfo);
            }}
            
            function drawCylinder(projection, view, model) {{
            twgl.setBuffersAndAttributes(gl, programInfo, cylinderBufferInfo);
        
            twgl.setUniforms(programInfo, {{
                u_color: color,
                u_lightDir: lightDir,
                u_projection: projection,
                u_view: view,
                u_model: model,
            }});
          
            twgl.drawBufferInfo(gl, cylinderBufferInfo);
            }}
            
            function drawCone(projection, view, model) {{
            twgl.setBuffersAndAttributes(gl, programInfo, truncatCylinderBufferInfo);
        
            twgl.setUniforms(programInfo, {{
                u_color: color,
                u_lightDir: lightDir,
                u_projection: projection,
                u_view: view,
                u_model: model,
            }});
          
            twgl.drawBufferInfo(gl, truncatCylinderBufferInfo);
            }}
            
            
            </script>
            
            """,
            width = 640,
            height = 640
        )
        
    def unuse(self):
        with st.expander("3D Motion Equation"):
            st.markdown("# 3D Motion Equation")
            st.markdown(
                "Use anthropometric data of a subject with bw=60 kg and bh=160 cm to define segment length, mass, position of center of mass, and moment of inertia of upper arm and lower arm as double pendulum model. Derive motion equation of double pendulum with shoulder and elbow joint dynamics. Solve the motion equation using RK IV integration method and perform passive movement test (active torques=0.0). Write your report of all steps of this assignment. By learning how to develop a 3d rendering using OpenGL, prepare to visualize your model of 3d movements. Your visualization will be a next topic of assignment."
            )
            st.markdown("## Anthropometric Calculation")
            st.image(
                "body_segment.png",
                caption="Body segment lengths expressed as a fraction of body height H . Source: David A. Winter - Biomechanics and Motor Control of Human Movement",
                width=450,
            )
            st.image(
                "anthropometric_data.png",
                caption="""Source Codes: M, Dempster via Miller and Nelson; Biomechanics of Sport, Lea and Febiger, Philadelphia, 1973. P, Dempster via Plagenhoef; Patterns of
                Human Motion, Prentice-Hall, Inc. Englewood Cliffs, NJ, 1971. L, Dempster via Plagenhoef from living subjects; Patterns of Human Motion, Prentice-Hall,
                Inc., Englewood Cliffs, NJ, 1971. C, Calculated.""",
            )
            st.markdown(
                """
                        Using the above figure, we can calculate the following values:     
            """
            )
            st.latex(
                r"""\begin{aligned}
                    l_1 &= Upper\;Arm\;Length \\ 
                    l_2 &= Lower\;Arm\;Length \\
                    l_{1p} &= Upper\;Arm\;Proximal\;Length \\ 
                    l_{2p} &= Lower\;Arm\;Proximal\;Length \\
                    I_1 & = Upper\;Arm\;Moment\;Of\;Inertia \\
                    I_2 & = Lower\;Arm\;Moment\;Of\;Inertia \\
                    m_1&= Upper\;Arm\;Mass\\ 
                    m_2&=Lower\;Arm\;Mass\\
                    \\
                    l_1&= 0.186H \\ 
                    l_2&= 0.146H\\
                    l_{1p} &= 0.436l_1 \\ 
                    &= 0.436\times 0.186\times H \\
                    &= 0.081096H\\
                    l_{2p} &= 0.430l_2 \\ 
                    &= 0.430\times 0.146\times H \\
                    &= 0.06278H\\
                    m_1&= 0.028\times M\\ 
                    m_2&= 0.016\times M\\ 
                    I_1 &= m_1(l_1\times 0.322)^2\\
                        &= 0.028\times M(0.186H\times 0.322)^2\\
                        &= 0.028\times M(0.059892H)^2\\
                        &= 0.000100437446592MH^2\\
                    I_2 &= m_2(l_2\times 0.303)^2\\
                        &= 0.016\times M(0.146H\times 0.303)^2\\
                        &= 0.000031312010304MH^2\\
                    \\
                    H&= 160\;cm\\
                    M&= 60\;kg\\
                    \\
                    l_1&= 0.186\times 160\;cm\\
                    l_2&= 0.146\times 160\;cm\\
                    l_{1p}&=  0.081096\times 160\;cm\\
                    l_{2p}&=  0.06278\times 160\;cm\\
                    m_1&= 0.028\times 60\;kg\\ 
                    m_2&= 0.016\times 60\;kg\\ 
                    I_1&=0.000100437446592(60\;kg)(1.6\;m)^2\\
                    I_2&=0.000031312010304(60\;kg)(1.6\;m)^2\\
                    \\
                    l_1&=  29.76\;cm\\
                    l_2&=  23.36\;cm\\
                    l_{1p}&=  12.97536\;cm\\
                    l_{2p}&=  10.0448\;cm\\
                    m_1&= 1.68\;kg\\ 
                    m_2&= 0.96\;kg\\ 
                    I_1&= 0.015427191796531202\;kgm^{2}\\
                    I_2&= 0.0048095247826944005\;kgm^{2}\\
                    
                    \end{aligned}"""
            )
            st.markdown("## Motion Equation")
            st.image("xyz.png")
            st.image("double_xyz.png")
            st.markdown("### Positions in Cartesian")
            st.latex(
                r"""
                    \begin{aligned}
                    x_1&=l_{1p}sin{\theta_1}cos{\varphi_1}\\
                    y_1&=l_{1p}sin{\theta_1}sin{\varphi_1}\\
                    z_1 &= -l_{1p}cos{\theta_1}\\
                    \\
                    x_2&=l_1sin{\theta_1}cos{\varphi_1}+l_{2p}sin{\theta_2}cos{\varphi_2}\\
                    y_2&=l_1sin{\theta_1}sin{\varphi_1}+l_{2p}sin{\theta_2}sin{\varphi_2}\\
                    z_2&= -l_1cos{\theta_1}-l_{2p}cos{\theta_2}\\
                    \\
                    \end{aligned}
                    """
            )
            st.markdown("### Velocity")
            st.latex(
                r"""
                    \begin{aligned}
                    \dot{x_1}&=l_{1p}(\dot{\theta_1}cos{\theta_1}cos{\varphi_1}-\dot{\varphi_1}sin{\theta_1}sin{\varphi_1})\\
                    \dot{y_1}&=l_{1p}(\dot{\theta_1}cos{\theta_1}sin{\varphi_1}+\dot{\varphi_1}sin{\theta_1}cos{\varphi_1})\\
                    \dot{z_1}&=l_{1p}\dot{\theta_1}sin{\theta_1}\\
                    \\
                    \dot{x_2}&=l_1(\dot{\theta_1}cos{\theta_1}cos{\varphi_1}-\dot{\varphi_1}sin{\theta_1}sin{\varphi_1})+l_{2p}(\dot{\theta_2}cos{\theta_2}cos{\varphi_2}-\dot{\varphi_2}sin{\theta_2}sin{\varphi_2})\\
                    \dot{y_2}&=l_1(\dot{\theta_1}cos{\theta_1}sin{\varphi_1}+\dot{\varphi_1}sin{\theta_1}cos{\varphi_1})+l_{2p}(\dot{\theta_2}cos{\theta_2}sin{\varphi_2}+\dot{\varphi_2}sin{\theta_2}cos{\varphi_2})\\
                    \dot{z_2}&=l_1\dot{\theta_1}sin{\theta_1}+l_{2p}\dot{\theta_2}sin{\theta_2}\\   
                    \end{aligned}
                    """
            )
            st.markdown("### Velocity Squared")
            st.latex(
                r"""
                    \begin{aligned}
                    \dot{x_1}^2&=l_{1p}^2((\dot{\theta_1}cos{\theta_1}cos{\varphi_1})^{2}+(\dot{\varphi_1}sin{\theta_1}sin{\varphi_1})^{2}-2\dot{\theta_1}cos{\theta_1}cos{\varphi_1}\dot{\varphi_1}sin{\theta_1}sin{\varphi_1})\\
                    \dot{y_1}^2&=l_{1p}^2((\dot{\theta_1}cos{\theta_1}sin{\varphi_1})^{2}+(\dot{\varphi_1}sin{\theta_1}cos{\varphi_1})^{2}+2\dot{\theta_1}cos{\theta_1}sin{\varphi_1}\dot{\varphi_1}sin{\theta_1}cos{\varphi_1})\\
                    \dot{z_1}^2&=l_{1p}^2\dot{\theta_1^2}sin^2{\theta_1}\\
                    \\
                    \dot{x_2}^2&=\quad l_{1}^2((\dot{\theta_1}cos{\theta_1}cos{\varphi_1})^{2}+(\dot{\varphi_1}sin{\theta_1}sin{\varphi_1})^{2}-2\dot{\theta_1}cos{\theta_1}cos{\varphi_1}\dot{\varphi_1}sin{\theta_1}sin{\varphi_1})\\
                        &\quad+l_{2p}^2((\dot{\theta_2}cos{\theta_2}cos{\varphi_2})^{2}+(\dot{\varphi_2}sin{\theta_2}sin{\varphi_2})^{2}-2\dot{\theta_2}cos{\theta_2}cos{\varphi_2}\dot{\varphi_2}sin{\theta_2}sin{\varphi_2})\\
                        &\quad+2l_{1}l_{2p}(\dot{\theta_1}cos{\theta_1}cos{\varphi_1}-\dot{\varphi_1}sin{\theta_1}sin{\varphi_1})(\dot{\theta_2}cos{\theta_2}cos{\varphi_2}-\dot{\varphi_2}sin{\theta_2}sin{\varphi_2})\\
                    \dot{y_2}^2&=\quad l_{1}^2((\dot{\theta_1}cos{\theta_1}sin{\varphi_1})^{2}+(\dot{\varphi_1}sin{\theta_1}cos{\varphi_1})^{2}+2\dot{\theta_1}cos{\theta_1}sin{\varphi_1}\dot{\varphi_1}sin{\theta_1}cos{\varphi_1})\\
                        &\quad+l_{2p}^2((\dot{\theta_2}cos{\theta_2}sin{\varphi_2})^{2}+(\dot{\varphi_2}sin{\theta_2}cos{\varphi_2})^{2}+2\dot{\theta_2}cos{\theta_2}sin{\varphi_2}\dot{\varphi_2}sin{\theta_2}cos{\varphi_2})\\
                        &\quad+2l_{1}l_{2p}(\dot{\theta_1}cos{\theta_1}sin{\varphi_1}+\dot{\varphi_1}sin{\theta_1}cos{\varphi_1})(\dot{\theta_2}cos{\theta_2}sin{\varphi_2}+\dot{\varphi_2}sin{\theta_2}cos{\varphi_2})\\
                    \dot{z_2}^2&=(l_{1}\dot{\theta_1}sin{\theta_1})^{2}+(l_{2p}\dot{\theta_2}sin{\theta_2})^{2}+2l_{1}\dot{\theta_1}sin{\theta_1}l_{2p}\dot{\theta_2}sin{\theta_2}\\
                    \\
                        
                        
                    \dot{x_1}^2+\dot{y_1}^2+\dot{z_1}^2&=\quad l_{1p}^2((\dot{\theta_1}cos{\theta_1}cos{\varphi_1})^{2}+(\dot{\varphi_1}sin{\theta_1}sin{\varphi_1})^{2}-2\dot{\theta_1}cos{\theta_1}cos{\varphi_1}\dot{\varphi_1}sin{\theta_1}sin{\varphi_1})\\
                                                    &\quad+l_{1p}^2((\dot{\theta_1}cos{\theta_1}sin{\varphi_1})^{2}+(\dot{\varphi_1}sin{\theta_1}cos{\varphi_1})^{2}+2\dot{\theta_1}cos{\theta_1}sin{\varphi_1}\dot{\varphi_1}sin{\theta_1}cos{\varphi_1})\\
                                                    &\quad+l_{1p}^2\dot{\theta_1^2}sin^2{\theta_1}\\
                                                        &=l_{1p}^2(\dot{\theta_1}^2+\dot{\varphi_1}^{2}sin^2{\theta_1})\\\\
                    \dot{x_2}^2+\dot{y_2}^2+\dot{z_2}^2&=\quad l_{1}^2((\dot{\theta_1}cos{\theta_1}cos{\varphi_1})^{2}+(\dot{\varphi_1}sin{\theta_1}sin{\varphi_1})^{2}-2\dot{\theta_1}cos{\theta_1}cos{\varphi_1}\dot{\varphi_1}sin{\theta_1}sin{\varphi_1})\\
                        &\quad+l_{2p}^2((\dot{\theta_2}cos{\theta_2}cos{\varphi_2})^{2}+(\dot{\varphi_2}sin{\theta_2}sin{\varphi_2})^{2}-2\dot{\theta_2}cos{\theta_2}cos{\varphi_2}\dot{\varphi_2}sin{\theta_2}sin{\varphi_2})\\
                        &\quad+2l_{1}l_{2p}(\dot{\theta_1}cos{\theta_1}cos{\varphi_1}-\dot{\varphi_1}sin{\theta_1}sin{\varphi_1})(\dot{\theta_2}cos{\theta_2}cos{\varphi_2}-\dot{\varphi_2}sin{\theta_2}sin{\varphi_2})\\
                        &\quad+l_{1}^2((\dot{\theta_1}cos{\theta_1}sin{\varphi_1})^{2}+(\dot{\varphi_1}sin{\theta_1}cos{\varphi_1})^{2}+2\dot{\theta_1}cos{\theta_1}sin{\varphi_1}\dot{\varphi_1}sin{\theta_1}cos{\varphi_1})\\
                        &\quad+l_{2p}^2((\dot{\theta_2}cos{\theta_2}sin{\varphi_2})^{2}+(\dot{\varphi_2}sin{\theta_2}cos{\varphi_2})^{2}+2\dot{\theta_2}cos{\theta_2}sin{\varphi_2}\dot{\varphi_2}sin{\theta_2}cos{\varphi_2})\\
                        &\quad+2l_{1}l_{2p}(\dot{\theta_1}cos{\theta_1}sin{\varphi_1}+\dot{\varphi_1}sin{\theta_1}cos{\varphi_1})(\dot{\theta_2}cos{\theta_2}sin{\varphi_2}+\dot{\varphi_2}sin{\theta_2}cos{\varphi_2})\\
                        &\quad+(l_{1}\dot{\theta_1}sin{\theta_1})^{2}+(l_{2p}\dot{\theta_2}sin{\theta_2})^{2}+2l_{1}\dot{\theta_1}sin{\theta_1}l_{2p}\dot{\theta_2}sin{\theta_2}\\
                        &=\quad l_{1}^2(\dot{\theta_1}^{2}+(\dot{\varphi_1}sin{\theta_1})^{2})+l_{2p}^2(\dot{\theta_2}^{2}+(\dot{\varphi_2}sin{\theta_2})^{2})\\
                        &\quad+2l_{1}l_{2p}(\dot{\theta_2}cos{\theta_2}(\dot{\theta_1}cos{\theta_1}cos{(\varphi_1-\varphi_2)}-\dot{\varphi_1}sin{\theta_1}sin{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad+\dot{\varphi_2}sin{\theta_2}(\dot{\theta_1}cos{\theta_1}sin{(\varphi_1-\varphi_2)}+\dot{\varphi_1}sin{\theta_1}cos{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad+\dot{\theta_1}\dot{\theta_2}sin{\theta_1}sin{\theta_2})\\
                        
                    \end{aligned}
                    """
            )

            st.markdown("### Kinetic Energy and Potential Energy")
            st.latex(
                r"""
                    \begin{aligned}
                    EK_1&=\frac{1}{2}m_1v_1^2+\frac{1}{2}I_1\dot{\theta_1}^{2}\\
                    EK_2&=\frac{1}{2}m_2v_2^2+\frac{1}{2}I_2\dot{\theta_2}^{2}\\
                    EK&=EK_1+EK_2\\
                    EK&=\frac{1}{2}(m_1v_1^2+m_2v_2^2+I_1\dot{\theta_1}^{2}+I_2\dot{\theta_2}^{2})\\
                    v_1^2&=\dot{x_1}^2+\dot{y_1}^2+\dot{z_1}^2\\
                    v_2^2&=\dot{x_2}^2+\dot{y_2}^2+\dot{z_2}^2\\
                    \\
                    EP_1&=m_1gh_1^2\\
                    EP_2&=m_2gh_2^2\\
                    EP&=EP_1+EP_2\\
                    EP&=g(m_1h_1+m_2h_2)\\
                    h_1&=0.818H-l_{1p}cos{\theta_1}\\
                    h_2&=0.818H-l_1cos{\theta_1}-l_{2p}cos{\theta_2}
                    \\
                    \end{aligned}
                    """
            )
            st.markdown("### Lagrange Function")
            st.latex(
                r"""
                    \begin{aligned}
                    L&=EK-EP\\
                    L&=\frac{1}{2}(m_1v_1^2+m_2v_2^2+I_1\dot{\theta_1}^{2}+I_2\dot{\theta_2}^{2})-g(m_1h_1+m_2h_2)\\
                    
                    L&=\frac{1}{2}(m_1(l_{1p}^2(\dot{\theta_1}^2+\dot{\varphi_1}^{2}sin^2{\theta_1}))\\
                        &\qquad +m_2(l_{1}^2(\dot{\theta_1}^{2}+(\dot{\varphi_1}sin{\theta_1})^{2})+l_{2p}^2(\dot{\theta_2}^{2}+(\dot{\varphi_2}sin{\theta_2})^{2})\\
                        &\quad\qquad\qquad+2l_{1}l_{2p}(\dot{\theta_2}cos{\theta_2}(\dot{\theta_1}cos{\theta_1}cos{(\varphi_1-\varphi_2)}-\dot{\varphi_1}sin{\theta_1}sin{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\qquad\qquad+\dot{\varphi_2}sin{\theta_2}(\dot{\theta_1}cos{\theta_1}sin{(\varphi_1-\varphi_2)}+\dot{\varphi_1}sin{\theta_1}cos{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\qquad\qquad+\dot{\theta_1}\dot{\theta_2}sin{\theta_1}sin{\theta_2}))\\
                        &\qquad +I_{1}\dot{\theta_1}^{2}+I_{2}\dot{\theta_2}^{2})\\
                        &\quad -g(m_{1}(0.818H-l_{1p}cos{\theta_1})+m_{2}(0.818H-l_1cos{\theta_1}-l_{2p}cos{\theta_2}))\\
                    \end{aligned}
                    """
            )
            st.markdown("### Lagrange Equation")
            st.latex(
                r"""
                    \begin{aligned}
                    \frac{d}{dt} \frac{\partial L}{\partial \dot{\alpha}}-\frac{\partial L}{\partial \alpha}&=\tau\\
                    \\
                    \frac{\partial L}{\partial \theta_1}&=\frac{1}{2}(2m_1l_{1p}^2\dot{\varphi_1}^{2}sin{\theta_1}cos{\theta_1}\\
                        &\qquad +m_2(2l_{1}^2\dot{\varphi_1}^{2}sin{\theta_1}cos{\theta_1}\\
                        &\quad\qquad\qquad+2l_{1}l_{2p}(\dot{\theta_2}cos{\theta_2}(-\dot{\theta_1}sin{\theta_1}cos{(\varphi_1-\varphi_2)}-\dot{\varphi_1}cos{\theta_1}sin{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\qquad\qquad+\dot{\varphi_2}sin{\theta_2}(-\dot{\theta_1}sin{\theta_1}sin{(\varphi_1-\varphi_2)}+\dot{\varphi_1}cos{\theta_1}cos{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\qquad\qquad+\dot{\theta_1}\dot{\theta_2}cos{\theta_1}sin{\theta_2}))\\
                        &\quad -g(m_{1}l_{1p}sin{\theta_1}+m_{2}(l_1sin{\theta_1})\\
                    
                        
                        
                        
                    \\\frac{\partial L}{\partial \dot{\theta_1}}&=\frac{1}{2}(2m_1l_{1p}^2\dot{\theta_1}
                        +m_2(2l_{1}^2\dot{\theta_1}
                        +2l_{1}l_{2p}(\dot{\theta_2}cos{\theta_2}(cos{\theta_1}cos{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\qquad\qquad\qquad\qquad\qquad+\dot{\varphi_2}sin{\theta_2}(cos{\theta_1}sin{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\qquad\qquad\qquad\qquad\qquad+\dot{\theta_2}sin{\theta_1}sin{\theta_2}))\\
                        &\qquad +2I_{1}\dot{\theta_1})\\
                        
                    
                        
                    \\
                        
                        
                        
                        
                    \frac{d}{dt} \frac{\partial L}{\partial \dot{\theta_1}}&=\frac{1}{2}(2m_1l_{1p}^2\ddot{\theta_1}\\
                        &\qquad + m_2(2l_{1}^2\ddot{\theta_1}\\
                        &\qquad\qquad+2l_{1}l_{2p}(((\ddot{\theta_2}cos{\theta_2}-\dot{\theta_2}sin{\theta_2})(cos{\theta_1}cos{(\varphi_1-\varphi_2)})+\dot{\theta_2}cos{\theta_2}(-sin{\theta_1}cos{(\varphi_1-\varphi_2)}))\\
                        &\quad\qquad\qquad\qquad+(\ddot{\varphi_2}sin{\theta_2}+\dot{\varphi_2}cos{\theta_2})(cos{\theta_1}sin{(\varphi_1-\varphi_2)})+\dot{\varphi_2}sin{\theta_2}(-sin{\theta_1}sin{(\varphi_1-\varphi_2)})\\
                        &\quad\qquad\qquad\qquad+\ddot{\theta_2}sin{\theta_1}sin{\theta_2}+\dot{\theta_2}(cos{\theta_1}sin{\theta_2}+sin{\theta_1}cos{\theta_2})))\\
                        &\qquad +2I_{1}\ddot{\theta_1})\\
                        \\
                    
                        \\
                    \frac{d}{dt} \frac{\partial L}{\partial \dot{\theta_1}}-\frac{\partial L}{\partial \theta_1}&=
                    \ddot{\theta_1}(m_1l_{1p}^{2}+m_2l_1^{2}+I_1)\\
                    &+\ddot{\theta_2}(m_2l_1l_{2p}(cos{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)}+sin{\theta_1}sin{\theta_2}))\\
                    &+\dot{\theta_2}(m_2l_1l_{2p}(sin{(\theta_1+\theta_2)}(1-cos{(\varphi_1-\varphi_2)})+\dot{\theta_1}sin{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)}+\dot{\varphi_1}cos{\theta_1}cos{\theta_2}sin{(\varphi_1-\varphi_2)}-\dot{\theta_1}cos{\theta_1}sin{\theta_2}))\\
                    &+\ddot{\varphi_2}(m_2l_1l_{2p}cos{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)})\\
                    &-\dot{\varphi_1}^{2}(sin{\theta_1}cos{\theta_1}(m_1l_{1p}^{2}+m_2l_1^{2}))\\
                    &+\dot{\varphi_2}(m_2l_1l_{2p}(cos{(\theta_1+\theta_2)}sin{(\varphi_1-\varphi_2)}+\dot{\theta_1}sin{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)}-\dot{\varphi_1}cos{\theta_1}sin{\theta_2}cos{(\varphi_1-\varphi_2)}))\\
                    &+g(m_{1}l_{1p}sin{\theta_1}+m_{2}l_1sin{\theta_1})
                    
                    \\\\\\
                    \frac{\partial L}{\partial \theta_2}&=\frac{1}{2}(
                        m_2(l_{2p}^{2}\varphi_{2}^{2}sin{\theta_2}cos{\theta_2}\\
                        &\qquad\qquad+2l_{1}l_{2p}(-\dot{\theta_2}sin{\theta_2}(\dot{\theta_1}cos{\theta_1}cos{(\varphi_1-\varphi_2)}-\dot{\varphi_1}sin{\theta_1}sin{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\qquad\qquad+\dot{\varphi_2}cos{\theta_2}(\dot{\theta_1}cos{\theta_1}sin{(\varphi_1-\varphi_2)}+\dot{\varphi_1}sin{\theta_1}cos{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\qquad\qquad+\dot{\theta_1}\dot{\theta_2}sin{\theta_1}cos{\theta_2}))\\
                        &\quad -g(m_{2}(l_{2p}sin{\theta_2}))\\
                    \\
                        
                        
                        
                    \frac{\partial L}{\partial \dot{\theta_2}}&=\frac{1}{2}(
                        m_2(2l_{2p}^2\dot{\theta_2}
                        +2l_{1}l_{2p}(cos{\theta_2}(\dot{\theta_1}cos{\theta_1}cos{(\varphi_1-\varphi_2)}-\dot{\varphi_1}sin{\theta_1}sin{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\qquad\qquad\qquad+\dot{\theta_1}sin{\theta_1}sin{\theta_2}))\\
                        &\qquad +2I_{2}\dot{\theta_2})\\
                        
                    \\
                        
                        
                        
                    \frac{d}{dt} \frac{\partial L}{\partial \dot{\theta_2}}&=\frac{1}{2}(
                        m_2(2l_{2p}^2\ddot{\theta_2}
                        +2l_{1}l_{2p}(-sin{\theta_2}(\dot{\theta_1}cos{\theta_1}cos{(\varphi_1-\varphi_2)}-\dot{\varphi_1}sin{\theta_1}sin{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\qquad\qquad\qquad+cos{\theta_2}((\ddot{\theta_1}cos{\theta_1}-\dot{\theta_1}sin{\theta_1})cos{(\varphi_1-\varphi_2)}\\
                        &\qquad\qquad\qquad\qquad\qquad\qquad\quad-(\ddot{\varphi_1}sin{\theta_1}+\dot{\varphi_1}cos{\theta_1})sin{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\qquad\qquad\qquad+\ddot{\theta_1}sin{\theta_1}sin{\theta_2}+\dot{\theta_1}(cos{\theta_1}sin{\theta_2}+sin{\theta_1}cos{\theta_2})))\\
                        &\qquad +2I_{2}\ddot{\theta_2})\\\\
                    
                    \\
                        
                    \frac{d}{dt} \frac{\partial L}{\partial \dot{\theta_2}}-\frac{\partial L}{\partial \theta_2}&=
                    \ddot{\theta_2}(m_2l_{2p}^{2}+I_2)\\
                    &+ \ddot{\theta_1}(m_2l_1l_{2p}(cos{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)}+sin{\theta_1}sin{\theta_2}))\\
                    &+ \dot{\theta_1}(m_2l_1l_{2p}(sin{(\theta_1+\theta_2)}(1-cos{(\varphi_1-\varphi_2)})+\dot{\theta_2}sin{\theta_2}cos{\theta_1}cos{(\varphi_1-\varphi_2)}-\dot{\varphi_2}cos{\theta_1}cos{\theta_2}sin{(\varphi_1-\varphi_2)}-\dot{\theta_2}sin{\theta_1}cos{\theta_2}))\\
                    &- \dot{\theta_2}(m_2l_1l_{2p}sin{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)})\\
                    &+ \ddot{\varphi_1}(-sin{\theta_1}cos{\theta_2}sin{(\varphi_1-\varphi_2)})\\
                    &+ \dot{\varphi_2}(-cos{(\theta_1+\theta_2)}sin{(\varphi_1-\varphi_2)}-m_2l_1l_{2p}\dot{\varphi_1}sin{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)})\\
                    &+ m_2l_{2p}sin{\theta_2}(g-\frac{1}{2}l_{2p}\varphi_{2}^{2}cos{\theta_2})
                    
                    \\\\\\
                    
                    
                    \\
                    \frac{\partial L}{\partial \varphi_1}&=\frac{1}{2}(
                        m_2(2l_{1}l_{2p}(\dot{\theta_2}cos{\theta_2}(-\dot{\theta_1}cos{\theta_1}sin{(\varphi_1-\varphi_2)}-\dot{\varphi_1}sin{\theta_1}cos{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\qquad+\dot{\varphi_2}sin{\theta_2}(\dot{\theta_1}cos{\theta_1}cos{(\varphi_1-\varphi_2)}-\dot{\varphi_1}sin{\theta_1}sin{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad)\\
                        &\qquad )\\
                        \\
                    \\
                    
                    
                    
                    
                    \frac{\partial L}{\partial \dot{\varphi_1}}&=\frac{1}{2}(2m_1l_{1p}^2\dot{\varphi_1}sin^2{\theta_1}
                        +m_2(2l_{1}^2\dot{\varphi_1}sin^{2}{\theta_1}
                        +2l_{1}l_{2p}(\dot{\theta_2}cos{\theta_2}(-sin{\theta_1}sin{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\qquad\qquad\qquad\qquad\qquad\qquad\qquad\qquad+\dot{\varphi_2}sin{\theta_2}(sin{\theta_1}cos{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\qquad\qquad\qquad\qquad)\\
                        &\qquad) \\
                    
                    \\
                    
                    
                    
                    
                    
                    \frac{d}{dt} \frac{\partial L}{\partial \dot{\varphi_1}}&=\frac{1}{2}(2m_1l_{1p}^2(\ddot{\varphi_1}sin^2{\theta_1}+2\dot{\varphi_1}sin{\theta_1}cos{\theta_1})\\
                        &\qquad +m_2(2l_{1}^2(\ddot{\varphi_1}sin^2{\theta_1}+2\dot{\varphi_1}sin{\theta_1}cos{\theta_1})\\
                        &\quad\qquad\qquad+2l_{1}l_{2p}((\ddot{\theta_2}cos{\theta_2}-\dot{\theta_2}sin{\theta_2})(-sin{\theta_1}sin{(\varphi_1-\varphi_2)})+\dot{\theta_2}cos{\theta_2}(-cos{\theta_1}sin{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\qquad\qquad+(\ddot{\varphi_2}sin{\theta_2}+\dot{\varphi_2}cos{\theta_2})(sin{\theta_1}cos{(\varphi_1-\varphi_2)})+\dot{\varphi_2}sin{\theta_2}(cos{\theta_1}cos{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\quad)\\
                        &\qquad) \\\\
                    
                    \frac{d}{dt} \frac{\partial L}{\partial \dot{\varphi_1}}-\frac{\partial L}{\partial \varphi_1}&=
                    \ddot{\theta_2}(-m_{2}l_{1}l_{2p}cos{\theta_2}sin{\theta_1}sin{(\varphi_1-\varphi_2)})\\
                    &+ \dot{\theta_2}(m_{2}l_{1}l_{2p}(-cos{(\theta_1-\theta_2)}sin{(\varphi_1-\varphi_2)}+\dot{\theta_1}cos{\theta_1}cos{\theta_2}sin{(\varphi_1-\varphi_2)}+\dot{\varphi_1}sin{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)}))\\
                    &+ \ddot{\varphi_1}(m_1l_{1p}^{2}sin^{2}{\theta_1}+m_2l_1^2sin^2{\theta_1})\\
                    &+ \dot{\varphi_1}(2m_1l_{1p}^{2}sin{\theta_1}cos{\theta_1}+2m_2l_{1}^{2}sin{\theta_1}cos{\theta_1})\\
                    &+ \ddot{\varphi_2}(m_2l_1l_{2p}sin{\theta_1}sin{\theta_2}cos{(\varphi_1-\varphi_2)})\\
                    &+ \dot{\varphi_2}(m_2l_1l_{2p}(sin{(\theta_1+\theta_2)}cos{(\varphi_1-\varphi_2)}-\dot{\theta_1}cos{\theta_1}sin{\theta_2}cos{(\varphi_1-\varphi_2)}+\dot{\varphi_1}sin{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)}))\\
                    
                    \\\\\\

                    
                    \\
                    \frac{\partial L}{\partial \varphi_2}&=\frac{1}{2}(
                        m_2(
                        2l_{1}l_{2p}(\dot{\theta_2}cos{\theta_2}(-\dot{\theta_1}cos{\theta_1}sin{(\varphi_2-\varphi_1)}+\dot{\varphi_1}sin{\theta_1}cos{(\varphi_2-\varphi_1)})\\
                        &\qquad\qquad\qquad+\dot{\varphi_2}sin{\theta_2}(-\dot{\theta_1}cos{\theta_1}cos{(\varphi_2-\varphi_1)}-\dot{\varphi_1}sin{\theta_1}sin{(\varphi_2-\varphi_1)})\\
                        &\qquad\qquad\qquad\quad)\\
                        &\qquad\qquad )\\
                        &\qquad) \\
                    \\
                    
                    
                    
                    \frac{\partial L}{\partial \dot{\varphi_2}}&=\frac{1}{2}(
                        m_2(2l_{2p}^2\dot{\varphi_2}sin^{2}{\theta_2}
                    +2l_{1}l_{2p}(
                        sin{\theta_2}(\dot{\theta_1}cos{\theta_1}sin{(\varphi_1-\varphi_2)}+\dot{\varphi_1}sin{\theta_1}cos{(\varphi_1-\varphi_2)})))\\
                        
                    \\
                    
                    
                    
                    
                    
                    \frac{d}{dt} \frac{\partial L}{\partial \dot{\varphi_2}}&=\frac{1}{2}(
                        m_2(2l_{2p}^2(\ddot{\varphi_2}sin^{2}{\theta_2}+2\dot{\varphi_2}sin{\theta_2}cos{\theta_2})\\
                        &\qquad\qquad+2l_{1}l_{2p}(
                        cos{\theta_2}(\dot{\theta_1}cos{\theta_1}sin{(\varphi_1-\varphi_2)}+\dot{\varphi_1}sin{\theta_1}cos{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\qquad\qquad +sin{\theta_2}((\ddot{\theta_1}cos{\theta_1}-\dot{\theta_1}sin{\theta_1})sin{(\varphi_1-\varphi_2)}\\
                        &\qquad\qquad\qquad\qquad\qquad +(\ddot{\varphi_1}sin{\theta_1}+\dot{\varphi_1}cos{\theta_1})cos{(\varphi_1-\varphi_2)})\\
                        &\qquad\qquad\qquad\qquad)\\
                        &\qquad )\\\\
                        
                    
                        
                    \frac{d}{dt} \frac{\partial L}{\partial \dot{\varphi_2}}-\frac{\partial L}{\partial \varphi_2}&=\ddot{\theta_1}(m_2l_{1}l_{2p}cos{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)})\\
                                                                                                                &+\dot{\theta_1}(m_2l_{1}l_{2p}(cos{(\theta_1+\theta_2)}sin{(\varphi_1-\varphi_2)}+\dot{\theta_2}cos{\theta_1}cos{\theta_2}sin{(\varphi_2-\varphi_1)}+\dot{\varphi_2}cos{\theta_1}sin{\theta_2}cos{(\varphi_2-\varphi_1)}))\\
                                                                                                                &+\ddot{\varphi_1}(m_2l_1l_{2p}sin{\theta_1}sin{\theta_2}cos{(\varphi_1-\varphi_2)})\\
                                                                                                                &+\dot{\varphi_1}(m_2l_1l_{2p}(sin{(\theta_1+\theta_2)}cos{(\varphi_1-\varphi_2)}+\dot{\varphi_2}sin{\theta_1}sin{\theta_2}sin{(\varphi_2-\varphi_1)}-\dot{\theta_2}sin{\theta_1}cos{\theta_2}cos(\varphi_2-\varphi_1){})\\
                                                                                                                &+\ddot{\varphi_2}(m_2l_{2p}^2sin^{2}{\theta_2})\\
                                                                                                                &+\dot{\varphi_2}(2m_2l_{2p}^2sin{\theta_2}cos{\theta_2})\\
                    
                    
                    \\\\\\
                    
                    
                    
                    
                    \end{aligned}
                    """
            )
            st.markdown("### Motion Equation")
            st.latex(
                r"""
                    \begin{aligned}
                    \frac{d}{dt} \frac{\partial L}{\partial \dot{\theta_1}}-\frac{\partial L}{\partial \theta_1}&=\tau_{\theta_1}\\
                        
                    \frac{d}{dt} \frac{\partial L}{\partial \dot{\theta_1}}-\frac{\partial L}{\partial \theta_1}&=
                    \ddot{\theta_1}(m_1l_{1p}^{2}+m_2l_1^{2}+I_1)\\
                    &+\ddot{\theta_2}(m_2l_1l_{2p}(cos{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)}+sin{\theta_1}sin{\theta_2}))\\
                    &+\dot{\theta_2}(m_2l_1l_{2p}(sin{(\theta_1+\theta_2)}(1-cos{(\varphi_1-\varphi_2)})+\dot{\theta_1}sin{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)}+\dot{\varphi_1}cos{\theta_1}cos{\theta_2}sin{(\varphi_1-\varphi_2)}-\dot{\theta_1}cos{\theta_1}sin{\theta_2}))\\
                    &+\ddot{\varphi_2}(m_2l_1l_{2p}cos{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)})\\
                    &-\dot{\varphi_1}^{2}(sin{\theta_1}cos{\theta_1}(m_1l_{1p}^{2}+m_2l_1^{2}))\\
                    &+\dot{\varphi_2}(m_2l_1l_{2p}(cos{(\theta_1+\theta_2)}sin{(\varphi_1-\varphi_2)}+\dot{\theta_1}sin{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)}-\dot{\varphi_1}cos{\theta_1}sin{\theta_2}cos{(\varphi_1-\varphi_2)}))\\
                    &+g(m_{1}l_{1p}sin{\theta_1}+m_{2}l_1sin{\theta_1})\\\\
                    
                    \ddot{\theta_1}&=
                    \frac{\tau_{\theta_1}-
                    \begin{pmatrix}
                    
                    +\ddot{\theta_2}(m_2l_1l_{2p}(cos{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)}+sin{\theta_1}sin{\theta_2}))\\
                    +\dot{\theta_2}(m_2l_1l_{2p}(sin{(\theta_1+\theta_2)}(1-cos{(\varphi_1-\varphi_2)})+\dot{\theta_1}sin{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)}+\dot{\varphi_1}cos{\theta_1}cos{\theta_2}sin{(\varphi_1-\varphi_2)}-\dot{\theta_1}cos{\theta_1}sin{\theta_2}))\\
                    +\ddot{\varphi_2}(m_2l_1l_{2p}cos{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)})\\
                    -\dot{\varphi_1}^{2}(sin{\theta_1}cos{\theta_1}(m_1l_{1p}^{2}+m_2l_1^{2}))\\
                    +\dot{\varphi_2}(m_2l_1l_{2p}(cos{(\theta_1+\theta_2)}sin{(\varphi_1-\varphi_2)}+\dot{\theta_1}sin{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)}-\dot{\varphi_1}cos{\theta_1}sin{\theta_2}cos{(\varphi_1-\varphi_2)}))\\
                    g(m_{1}l_{1p}sin{\theta_1}+m_{2}l_1sin{\theta_1}) \\
                    
                    \end{pmatrix}}{(m_1l_{1p}^{2}+m_2l_1^{2}+I_1)}\\\\\\
                    
                    \frac{d}{dt} \frac{\partial L}{\partial \dot{\theta_2}}-\frac{\partial L}{\partial \theta_2}&=\tau_{\theta_2}\\
                    \frac{d}{dt} \frac{\partial L}{\partial \dot{\theta_2}}-\frac{\partial L}{\partial \theta_2}&=
                    \ddot{\theta_2}(m_2l_{2p}^{2}+I_2)\\
                    &+ \ddot{\theta_1}(m_2l_1l_{2p}(cos{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)}+sin{\theta_1}sin{\theta_2}))\\
                    &+ \dot{\theta_1}(m_2l_1l_{2p}(sin{(\theta_1+\theta_2)}(1-cos{(\varphi_1-\varphi_2)})+\dot{\theta_2}sin{\theta_2}cos{\theta_1}cos{(\varphi_1-\varphi_2)}-\dot{\varphi_2}cos{\theta_1}cos{\theta_2}sin{(\varphi_1-\varphi_2)}-\dot{\theta_2}sin{\theta_1}cos{\theta_2}))\\
                    &- \dot{\theta_2}(m_2l_1l_{2p}sin{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)})\\
                    &+ \ddot{\varphi_1}(-sin{\theta_1}cos{\theta_2}sin{(\varphi_1-\varphi_2)})\\
                    &+ \dot{\varphi_2}(-cos{(\theta_1+\theta_2)}sin{(\varphi_1-\varphi_2)}-m_2l_1l_{2p}\dot{\varphi_1}sin{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)})\\
                    &+ m_2l_{2p}sin{\theta_2}(g-\frac{1}{2}l_{2p}\varphi_{2}^{2}cos{\theta_2})\\\\
                    
                    \ddot{\theta_2}&=
                    \frac{\tau_{\theta_2}-
                    \begin{pmatrix}
                    +\ddot{\theta_1}(m_2l_1l_{2p}(cos{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)}+sin{\theta_1}sin{\theta_2}))\\
                    +\dot{\theta_1}(m_2l_1l_{2p}(sin{(\theta_1+\theta_2)}(1-cos{(\varphi_1-\varphi_2)})+\dot{\theta_2}sin{\theta_2}cos{\theta_1}cos{(\varphi_1-\varphi_2)}-\dot{\varphi_2}cos{\theta_1}cos{\theta_2}sin{(\varphi_1-\varphi_2)}-\dot{\theta_2}sin{\theta_1}cos{\theta_2}))\\
                    - \dot{\theta_2}(m_2l_1l_{2p}sin{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)})\\
                    + \ddot{\varphi_1}(-sin{\theta_1}cos{\theta_2}sin{(\varphi_1-\varphi_2)})\\
                    +\dot{\varphi_2}(-cos{(\theta_1+\theta_2)}sin{(\varphi_1-\varphi_2)}-m_2l_1l_{2p}\dot{\varphi_1}sin{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)})\\
                    + m_2l_{2p}sin{\theta_2}(g-\frac{1}{2}l_{2p}\varphi_{2}^{2}cos{\theta_2})\\
                    
                    \end{pmatrix}}{(m_2l_{2p}^{2}+I_2)}\\\\\\
                        
                    \frac{d}{dt} \frac{\partial L}{\partial \dot{\varphi_1}}-\frac{\partial L}{\partial \varphi_1}&=\tau_{\varphi_1}\\
                    \frac{d}{dt} \frac{\partial L}{\partial \dot{\varphi_1}}-\frac{\partial L}{\partial \varphi_1}&=
                    \ddot{\theta_2}(-m_{2}l_{1}l_{2p}cos{\theta_2}sin{\theta_1}sin{(\varphi_1-\varphi_2)})\\
                    &+ \dot{\theta_2}(m_{2}l_{1}l_{2p}(-cos{(\theta_1-\theta_2)}sin{(\varphi_1-\varphi_2)}+\dot{\theta_1}cos{\theta_1}cos{\theta_2}sin{(\varphi_1-\varphi_2)}+\dot{\varphi_1}sin{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)}))\\
                    &+ \ddot{\varphi_1}(m_1l_{1p}^{2}sin^{2}{\theta_1}+m_2l_1^2sin^2{\theta_1})\\
                    &+ \dot{\varphi_1}(2m_1l_{1p}^{2}sin{\theta_1}cos{\theta_1}+2m_2l_{1}^{2}sin{\theta_1}cos{\theta_1})\\
                    &+ \ddot{\varphi_2}(m_2l_1l_{2p}sin{\theta_1}sin{\theta_2}cos{(\varphi_1-\varphi_2)})\\
                    &+ \dot{\varphi_2}(m_2l_1l_{2p}(sin{(\theta_1+\theta_2)}cos{(\varphi_1-\varphi_2)}-\dot{\theta_1}cos{\theta_1}sin{\theta_2}cos{(\varphi_1-\varphi_2)}+\dot{\varphi_1}sin{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)}))
                    
                    \\\\\ddot{\varphi_1}&=
                    \frac{\tau_{\varphi_1}-
                    \begin{pmatrix}
                + \ddot{\theta_2}(-m_{2}l_{1}l_{2p}cos{\theta_2}sin{\theta_1}sin{(\varphi_1-\varphi_2)})\\
                    +\dot{\theta_2}(m_{2}l_{1}l_{2p}(-cos{(\theta_1-\theta_2)}sin{(\varphi_1-\varphi_2)}+\dot{\theta_1}cos{\theta_1}cos{\theta_2}sin{(\varphi_1-\varphi_2)}+\dot{\varphi_1}sin{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)}))\\
                    + \dot{\varphi_1}(2m_1l_{1p}^{2}sin{\theta_1}cos{\theta_1}+2m_2l_{1}^{2}sin{\theta_1}cos{\theta_1})\\
                    + \ddot{\varphi_2}(m_2l_1l_{2p}sin{\theta_1}sin{\theta_2}cos{(\varphi_1-\varphi_2)})\\
                    + \dot{\varphi_2}(m_2l_1l_{2p}(sin{(\theta_1+\theta_2)}cos{(\varphi_1-\varphi_2)}-\dot{\theta_1}cos{\theta_1}sin{\theta_2}cos{(\varphi_1-\varphi_2)}+\dot{\varphi_1}sin{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)}))
                    
                    \end{pmatrix}}{(m_1l_{1p}^{2}sin^{2}{\theta_1}+m_2l_1^2sin^2{\theta_1})}\\\\\\
                    \frac{d}{dt} \frac{\partial L}{\partial \dot{\varphi_2}}-\frac{\partial L}{\partial \varphi_2}&=\tau_{\varphi_2}\\
                    \frac{d}{dt} \frac{\partial L}{\partial \dot{\varphi_2}}-\frac{\partial L}{\partial \varphi_2}&=\ddot{\theta_1}(m_2l_{1}l_{2p}cos{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)})\\
                                                                                                                &+\dot{\theta_1}(m_2l_{1}l_{2p}(cos{(\theta_1+\theta_2)}sin{(\varphi_1-\varphi_2)}+\dot{\theta_2}cos{\theta_1}cos{\theta_2}sin{(\varphi_2-\varphi_1)}+\dot{\varphi_2}cos{\theta_1}sin{\theta_2}cos{(\varphi_2-\varphi_1)}))\\
                                                                                                                &+\ddot{\varphi_1}(m_2l_1l_{2p}sin{\theta_1}sin{\theta_2}cos{(\varphi_1-\varphi_2)})\\
                                                                                                                &+\dot{\varphi_1}(m_2l_1l_{2p}(sin{(\theta_1+\theta_2)}cos{(\varphi_1-\varphi_2)}+\dot{\varphi_2}sin{\theta_1}sin{\theta_2}sin{(\varphi_2-\varphi_1)}-\dot{\theta_2}sin{\theta_1}cos{\theta_2}cos(\varphi_2-\varphi_1){})\\
                                                                                                                &+\ddot{\varphi_2}(m_2l_{2p}^2sin^{2}{\theta_2})\\
                                                                                                                &+\dot{\varphi_2}(2m_2l_{2p}^2sin{\theta_2}cos{\theta_2})\\
                    \\\\\ddot{\varphi_2}&=
                    \frac{\tau_{\varphi_2}-
                    \begin{pmatrix}
                    +\ddot{\theta_1}(m_2l_{1}l_{2p}cos{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)})\\
                    +\dot{\theta_1}(m_2l_{1}l_{2p}(cos{(\theta_1+\theta_2)}sin{(\varphi_1-\varphi_2)}+\dot{\theta_2}cos{\theta_1}cos{\theta_2}sin{(\varphi_2-\varphi_1)}+\dot{\varphi_2}cos{\theta_1}sin{\theta_2}cos{(\varphi_2-\varphi_1)}))\\
                    +\ddot{\varphi_1}(m_2l_1l_{2p}sin{\theta_1}sin{\theta_2}cos{(\varphi_1-\varphi_2)})\\
                    +\dot{\varphi_1}(m_2l_1l_{2p}(sin{(\theta_1+\theta_2)}cos{(\varphi_1-\varphi_2)}+\dot{\varphi_2}sin{\theta_1}sin{\theta_2}sin{(\varphi_2-\varphi_1)}-\dot{\theta_2}sin{\theta_1}cos{\theta_2}cos(\varphi_2-\varphi_1){})\\
                    +\dot{\varphi_2}(2m_2l_{2p}^2sin{\theta_2}cos{\theta_2})\\
                    \end{pmatrix}}{(m_2l_{2p}^2sin^{2}{\theta_2})}\\\\\\
                    
                    \end{aligned}
                    """
            )
            st.markdown("### Runge Kutta Method")
            st.latex(
                r"""
                    \begin{aligned}
                    \begin{pmatrix}
                    \tau_{\theta_1}\\
                        \tau_{\theta_2}\\
                            \tau_{\varphi_1}\\
                                \tau_{\varphi_2}\\
                    \end{pmatrix}
                    =0\\
                    \ddot{\theta_1}&=
                    \frac{0-
                    \begin{pmatrix}
                    
                    +\ddot{\theta_2}(m_2l_1l_{2p}(cos{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)}+sin{\theta_1}sin{\theta_2}))\\
                    +\dot{\theta_2}(m_2l_1l_{2p}(sin{(\theta_1+\theta_2)}(1-cos{(\varphi_1-\varphi_2)})+\dot{\theta_1}sin{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)}+\dot{\varphi_1}cos{\theta_1}cos{\theta_2}sin{(\varphi_1-\varphi_2)}-\dot{\theta_1}cos{\theta_1}sin{\theta_2}))\\
                    +\ddot{\varphi_2}(m_2l_1l_{2p}cos{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)})\\
                    -\dot{\varphi_1}^{2}(sin{\theta_1}cos{\theta_1}(m_1l_{1p}^{2}+m_2l_1^{2}))\\
                    +\dot{\varphi_2}(m_2l_1l_{2p}(cos{(\theta_1+\theta_2)}sin{(\varphi_1-\varphi_2)}+\dot{\theta_1}sin{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)}-\dot{\varphi_1}cos{\theta_1}sin{\theta_2}cos{(\varphi_1-\varphi_2)}))\\
                    g(m_{1}l_{1p}sin{\theta_1}+m_{2}l_1sin{\theta_1}) \\
                    
                    \end{pmatrix}}{(m_1l_{1p}^{2}+m_2l_1^{2}+I_1)}\\\\\\
                    \ddot{\theta_2}&=
                    \frac{0-
                    \begin{pmatrix}
                    +\ddot{\theta_1}(m_2l_1l_{2p}(cos{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)}+sin{\theta_1}sin{\theta_2}))\\
                    +\dot{\theta_1}(m_2l_1l_{2p}(sin{(\theta_1+\theta_2)}(1-cos{(\varphi_1-\varphi_2)})+\dot{\theta_2}sin{\theta_2}cos{\theta_1}cos{(\varphi_1-\varphi_2)}-\dot{\varphi_2}cos{\theta_1}cos{\theta_2}sin{(\varphi_1-\varphi_2)}-\dot{\theta_2}sin{\theta_1}cos{\theta_2}))\\
                    - \dot{\theta_2}(m_2l_1l_{2p}sin{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)})\\
                    + \ddot{\varphi_1}(-sin{\theta_1}cos{\theta_2}sin{(\varphi_1-\varphi_2)})\\
                    +\dot{\varphi_2}(-cos{(\theta_1+\theta_2)}sin{(\varphi_1-\varphi_2)}-m_2l_1l_{2p}\dot{\varphi_1}sin{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)})\\
                    + m_2l_{2p}sin{\theta_2}(g-\frac{1}{2}l_{2p}\varphi_{2}^{2}cos{\theta_2})\\
                    
                    \end{pmatrix}}{(m_2l_{2p}^{2}+I_2)}\\\\\\
                    \\\\\ddot{\varphi_1}&=
                    \frac{0-
                    \begin{pmatrix}
                + \ddot{\theta_2}(-m_{2}l_{1}l_{2p}cos{\theta_2}sin{\theta_1}sin{(\varphi_1-\varphi_2)})\\
                    +\dot{\theta_2}(m_{2}l_{1}l_{2p}(-cos{(\theta_1-\theta_2)}sin{(\varphi_1-\varphi_2)}+\dot{\theta_1}cos{\theta_1}cos{\theta_2}sin{(\varphi_1-\varphi_2)}+\dot{\varphi_1}sin{\theta_1}cos{\theta_2}cos{(\varphi_1-\varphi_2)}))\\
                    + \dot{\varphi_1}(2m_1l_{1p}^{2}sin{\theta_1}cos{\theta_1}+2m_2l_{1}^{2}sin{\theta_1}cos{\theta_1})\\
                    + \ddot{\varphi_2}(m_2l_1l_{2p}sin{\theta_1}sin{\theta_2}cos{(\varphi_1-\varphi_2)})\\
                    + \dot{\varphi_2}(m_2l_1l_{2p}(sin{(\theta_1+\theta_2)}cos{(\varphi_1-\varphi_2)}-\dot{\theta_1}cos{\theta_1}sin{\theta_2}cos{(\varphi_1-\varphi_2)}+\dot{\varphi_1}sin{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)}))
                    
                    \end{pmatrix}}{(m_1l_{1p}^{2}sin^{2}{\theta_1}+m_2l_1^2sin^2{\theta_1})}\\\\\\
                    \\\\\ddot{\varphi_2}&=
                    \frac{0-
                    \begin{pmatrix}
                    +\ddot{\theta_1}(m_2l_{1}l_{2p}cos{\theta_1}sin{\theta_2}sin{(\varphi_1-\varphi_2)})\\
                    +\dot{\theta_1}(m_2l_{1}l_{2p}(cos{(\theta_1+\theta_2)}sin{(\varphi_1-\varphi_2)}+\dot{\theta_2}cos{\theta_1}cos{\theta_2}sin{(\varphi_2-\varphi_1)}+\dot{\varphi_2}cos{\theta_1}sin{\theta_2}cos{(\varphi_2-\varphi_1)}))\\
                    +\ddot{\varphi_1}(m_2l_1l_{2p}sin{\theta_1}sin{\theta_2}cos{(\varphi_1-\varphi_2)})\\
                    +\dot{\varphi_1}(m_2l_1l_{2p}(sin{(\theta_1+\theta_2)}cos{(\varphi_1-\varphi_2)}+\dot{\varphi_2}sin{\theta_1}sin{\theta_2}sin{(\varphi_2-\varphi_1)}-\dot{\theta_2}sin{\theta_1}cos{\theta_2}cos(\varphi_2-\varphi_1){})\\
                    +\dot{\varphi_2}(2m_2l_{2p}^2sin{\theta_2}cos{\theta_2})\\
                    \end{pmatrix}}{(m_2l_{2p}^2sin^{2}{\theta_2})}\\\\\\
                    \frac{\partial^2 y}{\partial x^2}&= f(x,y,y')\\
                    k_1&=\frac{h}{2}f(x,y,y')\\
                    k_2&=\frac{h}{2}f\left( x+\frac{h}{2},y+\frac{h}{2}\left(y'+\frac{k1}{2}\right),y'+k_1\right)\\
                    k_3&=\frac{h}{2}f\left( x+\frac{h}{2},y+\frac{h}{2}\left(y'+\frac{k1}{2}\right),y'+k_2\right)\\
                    k_4&=\frac{h}{2}f\left( x+h,y+h\left(y'+k_3\right),y'+2k_3\right)\\
                    y_n&=y_{n-1}+h\left(y'_{n-1}+\frac{k_1+k_2+k_3}{3}\right)\\
                    y'_n&=y'_{n-1}+h\left(k_1+2k_2+2k_3+k_4\right)\\
                    \end{aligned}
                    """
            )

        c1, c2, c3, c4 = st.columns(4)
        H = c1.number_input("Height (cm)", value=160)
        M = c2.number_input("Mass (kg)", value=60)
        dt = c3.number_input("Time step (s)", value=0.1)
        duration = c4.number_input("Duration (s)", value=1)

        theta_1 = c1.number_input("Upper Arm Angle Theta (deg)", value=0)
        theta_2 = c2.number_input("Lower Arm Angle Theta (deg)", value=0)
        phi_1 = c3.number_input("Upper Arm Angular Phi (deg)", value=0)
        phi_2 = c4.number_input("Lower Arm Angular Phi (deg)", value=0)
        
        theta_1_dot = c1.number_input("Upper Arm Angle Theta Velocity (deg/s)", value=0)
        theta_2_dot = c2.number_input("Lower Arm Angle Theta Velocity (deg/s)", value=0)
        phi_1_dot = c3.number_input("Upper Arm Angular Phi Velocity (deg/s)", value=0)
        phi_2_dot = c4.number_input("Lower Arm Angular Phi Velocity (deg/s)", value=0)
        
        theta_1_dot_dot = c1.number_input("Upper Arm Angle Theta Acceleration (deg/s^2)", value=0)
        theta_2_dot_dot = c2.number_input("Lower Arm Angle Theta Acceleration (deg/s^2)", value=0)
        phi_1_dot_dot = c3.number_input("Upper Arm Angular Phi Acceleration (deg/s^2)", value=0)
        phi_2_dot_dot = c4.number_input("Lower Arm Angular Phi Acceleration (deg/s^2)", value=0)
        
        tau_theta_1 = c1.number_input("Upper Arm Theta Torque (Nm)", value=0)
        tau_theta_2 = c2.number_input("Lower Arm Theta Torque (Nm)", value=0)
        tau_phi_1 = c3.number_input("Upper Arm Phi Torque (Nm)", value=0)
        tau_phi_2 = c4.number_input("Lower Arm Phi Torque (Nm)", value=0)
        
        simulation_input = {
            "H": H,
            "M": M,
            "dt": dt,
            "duration": duration,
            "theta_1":theta_1,
            "theta_2":theta_2,
            "phi_1":phi_1,
            "phi_2":phi_2,
            "theta_1_dot":theta_1_dot,
            "theta_2_dot":theta_2_dot,
            "phi_1_dot":phi_1_dot,
            "phi_2_dot":phi_2_dot,
            "theta_1_dot_dot":theta_1_dot_dot,
            "theta_2_dot_dot":theta_2_dot_dot,
            "phi_1_dot_dot":phi_1_dot_dot,
            "phi_2_dot_dot":phi_2_dot_dot,
            "tau_theta_1": tau_theta_1,
            "tau_theta_2": tau_theta_2,
            "tau_phi_1": tau_phi_1,
            "tau_phi_2": tau_phi_2,
        }
        debug = st.checkbox("Debug")
        motion_simulation = Simulation(simulation_input)
        if st.button("Run Simulation"):
            motion_simulation.simulate()
            st.write(motion_simulation.dynamic_array)
            motion_simulation.plot()
        if debug:
            st.write(motion_simulation.info())
if __name__ == "__main__":
    Main().main()
