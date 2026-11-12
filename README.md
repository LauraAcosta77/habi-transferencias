# Simulador de transferencias 

## Tecnologías utilizadas

- **Python:** lenguaje utilizado para desarrollar la lógica del sistema.
- **Flask:** framework utilizado para conectar el frontend con el backend y gestionar las solicitudes.
- **SQLite:** base de datos utilizada para almacenar las cuentas y los movimientos.
- **HTML:** utilizado para construir la estructura de la interfaz.

## 1. ¿Qué decisiones clave tomé y por qué?

Una de las primeras decisiones fue utilizar Python con Flask para desarrollar la lógica del sistema. Elegí estas herramientas porque permiten construir una aplicación web sin necesitar una estructura demasiado compleja para el alcance del proyecto.

También decidí utilizar SQLite para almacenar la información de las cuentas y los movimientos, ya que es una base de datos sencilla de configurar y suficiente para este proyecto.

Otra decisión fue manejar únicamente cantidades enteras y positivas. Como el sistema está pensado para trabajar con pesos colombianos, consideré que no era necesario aceptar valores decimales. Esto también simplifica los cálculos y evita trabajar con fracciones de peso.

Finalmente, elegí los cobros divididos como funcionalidad adicional, porque permiten representar situaciones cotidianas en las que varias personas comparten un gasto.

## 2. ¿Cómo me aseguré de que el sistema no pierda dinero?

Mi principal objetivo fue mantener la consistencia de los saldos. Para esto, tomé varias decisiones:

- Antes de realizar una transferencia, verifico que las cuentas existan y que el monto sea positivo.
- También verifico que la cuenta de origen tenga saldo suficiente para realizar el movimiento.
- Cuando se realiza una transferencia, el dinero que se descuenta de una cuenta debe ser exactamente el mismo que se agrega a la cuenta de destino.
- No permito ingresar cantidades negativas ni valores decimales.
- En los cobros divididos, distribuyo el valor de manera que la suma de las partes coincida exactamente con el total. Si hay pesos sobrantes por la división, los tengo en cuenta para que no desaparezcan.
- Cuando una persona registra un gasto que ya pagó por fuera del sistema, no descuento nuevamente el valor total de su cuenta. Los demás participantes deben pagarle su parte.

Estas validaciones buscan evitar saldos negativos, movimientos con valores inválidos y diferencias en las cantidades de dinero.

## 3. ¿Qué dejé por fuera y por qué?

Decidí concentrarme en las funcionalidades principales del reto y en una funcionalidad adicional, por lo que dejé por fuera algunas características que podrían ampliar el sistema:

- Inicio de sesión y autenticación de usuarios.
- Integración con bancos o plataformas de pago reales.
- Notificaciones automáticas cuando alguien recibe o debe dinero.
- Recuperación de contraseñas.
- Una interfaz adaptable y optimizada para todos los dispositivos.

No las implementé porque quería concentrarme primero en el funcionamiento de las cuentas, las transferencias, el historial y los cobros divididos.

## 4. ¿Qué haría diferente si tuviera más tiempo?

Si tuviera más tiempo, mejoraría la interfaz para hacerla más intuitiva y adaptable a diferentes dispositivos.

También implementaría un sistema de autenticación para que cada usuario pudiera acceder únicamente a su propia cuenta. Además, fortalecería las pruebas del sistema, especialmente en situaciones donde ocurren varias transferencias al mismo tiempo. También profundizaría en el manejo de transacciones de base de datos para asegurar que una operación se complete correctamente o se revierta por completo si ocurre algún error.

## 5. ¿Qué cosas no sé?

Todavía tengo aspectos por mejorar en programación. Una de mis principales dificultades es la sintaxis, especialmente en HTML. También estoy aprendiendo a utilizar Flask y a comprender mejor cómo se conecta el frontend con el backend. Aunque logré utilizarlo en este proyecto, todavía necesito practicar para tener mayor autonomía al desarrollar aplicaciones con esta herramienta. Además, quiero fortalecer mis conocimientos sobre el manejo de bases de datos.
Considero que estos son aspectos que puedo seguir desarrollando con práctica y experiencia.

## 6. ¿Qué asumí y por qué?

Para desarrollar el proyecto tuve en cuenta algunos supuestos:

- Los valores se manejan en pesos colombianos.
- Las cantidades de dinero deben ser números enteros y positivos.
- Cada cuenta pertenece a una persona y se identifica dentro del sistema.
- Las transferencias se realizan entre cuentas que ya existen en el sistema.
- En los cobros divididos, la persona que registra el gasto es quien ya realizó el pago por fuera del sistema.
- Los participantes deben pagar su parte al usuario que registró el gasto.
- Los cobros divididos se reparten en partes iguales entre los participantes seleccionados.


## 7. ¿Cómo utilicé la inteligencia artificial?

Utilicé ChatGPT como herramienta de apoyo durante diferentes etapas del desarrollo del proyecto.

Principalmente, la utilicé para orientarme en la estructura del proyecto, resolver dudas sobre Python, conectar el frontend con el backend y entender cómo trabajar con Flask y SQLite. También pedí ayuda con la parte de HTML, ya que todavía no manejo muy bien su sintaxis y estoy fortaleciendo mis conocimientos en esta área. De igual manera, recibí orientación sobre Flask, porque es una herramienta que estoy aprendiendo a utilizar y con la que todavía no tengo mucha experiencia.

La IA me ayudó a entender errores, revisar el código y proponer posibles soluciones. Sin embargo, no me limité a copiar las respuestas, ya que fui revisando las funcionalidades y tomando decisiones sobre lo que quería implementar. Por ejemplo, inicialmente le pedi que me ayudara a estructurar mi idea, en cuanto al orden, y el esquema que me dio traia informacion duplicada que entorpecia el sistema. La IA propuso colocar la consulta de saldos como una seccion independiente, pero decidi que esa funcionslidad podia estar en el mismo apartado de cuentas, por lo que decidí eliminar esa opción para evitar repetir información.

## 8. ¿Qué aprendí?

Durante el desarrollo de este proyecto aprendí mas sobre conectar diferentes partes de una aplicación web y a comprender mejor cómo se relacionan el frontend, el backend y una base de datos. También aprendí más sobre Flask, Python y SQLite, especialmente sobre cómo recibir información desde formularios, procesarla y almacenarla.
Lo más importante que aprendí durante este proyecto fue que, antes de empezar a programar, es necesario entender bien qué se está pidiendo y qué problema se quiere resolver. No se trata solamente de escribir código para cumplir con un enunciado, sino de analizar las necesidades, identificar qué funcionalidades tienen sentido y tomar decisiones que permitan construir una solución útil.

También aprendí que es importante pensar en las situaciones que pueden presentarse cuando alguien utiliza el sistema. Por ejemplo, no basta con permitir hacer transferencias, sino que hay que pensar en cómo evitar que el dinero se pierda, que se cobre dos veces o que los saldos queden incorrectos.