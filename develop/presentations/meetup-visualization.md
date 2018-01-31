# Presentacion meetup visualization

30 Jan 2018

## Resumen/esquema

### Denis
* TalkExp.
* SetFusion
* T + S
* EpistAid
* Moodplay

### Pablo
Ver hablado

### Denis
* Cierre


## Hablado

* Portada
   Yo les voy a presentar sobre el trabajo que he estado haciendo, sobre este aparato llamado Muse, ya veremos qué es, y su integración con moodplay, la plataforma que les acaba de mostrar el profesor Denis.
   (this?) Yo soy alumno de ingeniería civil en computación en la UC, y junto con...
   En esto hemos estado trabajando junto con el profesor, Raimundo otro alumno de pregrado, y también hemos colaborado con Rodrigo Cadiz profesor de la escuela y Constanza, alumna de magister.

* BCI
  - qué es BCI  
    BCI significa Brain Computer Interface, es decir un dispositivo que conecta cerebro y computador.
    ¿y qué hace? este es un modelo muy simplificado de lo que permite un dispositivo BCI, se puede realizar acciones sólo con el cerebro, o también mandar la actividad cerebral que detecta; y por su parte el pc puede entregar feedback de algún tipo al usuario.
    Cabe destacar que en vez del pc podría ser, por ejemplo, una silla de ruedas, que contenga todo un sistema embebido para poder recibir señales desde el cerebro del usuario, y así la persona que esté en la silla de ruedas puede moverla sólo con la mente.

  - Se quiere incorporar BCI a moodplay
    Para que tengan en mente, lo que se quiere hacer es integrar una interfaz BCI con moodplay, y en particular integrar la interfaz para mejorar la recomendación de música al usuario. Para ir adelantando, se puede detectar cómo se encuentra mentalmente y según eso hacer o apoyar la recomendación.

  - fMRi vs EEG
    Bueno, dentro de las mediciones que se pueden hacer del cerebro hay dos formas ampliamente usadas, que son fMRI, una resonancia magnética; y por otro lado EEG, y electro-encefalograma. El fMRI mide potenciales magnéticos en la sangre, y con eso detecta aumento de oxígeno lo que significa actividad cerebral; se usan estas máquinas de aquí. Por otra parte, en EEG se miden potenciales eléctricos en la superficie de la cabeza, con sensores como se ve en esta imagen, y lo que se detecta es la actividad eléctrica agregada de muchas neuronas. También, mencionar que los EEG reciben actividad mediante varios canales, que son puntos donde se mide la actividad, que son estos sensores que se colocan aquí en la cabeza.
    Nosotros estamos trabajando actualmente con EEG, que es menos invasivo

  - dispositivos
    Existen distintos dispositivos EEG en el mercado, algunos destinados a laboratorio y otros a uso común. Está por ejemplo el emotiv, que tiene dos versiones con 5 y 14 canales; está esta marca ANT Neuro, que tiene varios dispositivos desde 8 hasta 256 canales; está NeuroSky que tiene sólo 1 canal; y muchos otros. Existen muchos dispositivos en el mercado, casi para todos los gustos.
    Entre los dispositivos de uso más común está el Muse, que es este que está aquí.

* Muse
  - Dispositivo
    El muse es un dispositivo que se vende para realizar meditación, viene con una app de celular que se conecta con el dispositivo mediante bluetooth; y te va dando feedback de qué tan relajado estás, así te ayuda a que medites y te relajes.
    El muse tiene 4 electrodos + 1 de referencia, en total 5. Si vemos aquí, es una cabeza mirada desde arriba [indicar nariz y orejas], son 2 canales en la frente y 2 canales detrás de las orejas; y el canal de referencia está aquí en la frente.
    Existen 2 versiones del Muse, 2014 y 2016. Para la 2014 existe un software para computador hecho para investigadores que te permite visualizar las ondas del usuario en el momento y grabar los datos a distintos formatos. Además tiene una librería para desarrolladores puedan hacer aplicaciones propias con el muse. Nosotros tenemos la versión 2016, y no existe nada de esto para esta versión. Bueno hace un tiempo lanzaron una, pero al parecer no es muy buena y existe sólo para windows. Así que parte de mi trabajo fue desarrollar todo el ambiente para recibir señales del dispositivo y procesarlas.

  - desarrollo API
    El software que desarrollé es de la siguiente manera. Hay un programa en python que se encarga de procesar las señales del dispositivo y guardar datos si es necesario, y luego las manda a otro programa que está en javascript para poder ser página web, que se encarga de la visualización y la interfaz de usuario. Así, este programa web se puede reemplazar por el moodplay que también es una página web.

  - raw eeg
    Ahora vamos a pasar a una demo de las ondas EEG que recibe el dispositivo.
    [Colocar a voluntario]
    Se comienza el programa en python que recibe las señales, luego vamos a la página web que muestra los datos.
    Aquí tenemos la onda en el tiempo. En el eje x tenemos el tiempo y en el eje y tenemos el voltaje de las señales que nos llegan. Cada color es un canal de los que les mostré, vemos que recibe los 4 canales más el de referencia, podemos desactivarlo aquí. Aquí se pueden mover los ejes.
    Vemos también que si la persona se mueve mucho o parpadea, la señal se ve bastante afectada por ruido.

  - TF-analysis (x4 diapos)
    + qué hacer con EEG
      Como vimos, la señal EEG es ruidosa y no nos muestra mucha información a simple vista.
      Un análisis muy común que se hace de EEG es un análisis de frecuencia que nos mostrará información más útil de la onda que estamos mirando
    + Suma de ondas
      EEG es una composición de ondas, qué significa esto? Supongamos tenemos estas dos ondas simples de acá, la primera es de baja frecuencia y baja potencia, mientras que la segunda es de mayor potencia y de mayor frecuencia. (La frecuencia nos indica qué tan rápido va una onda, la potencia se ve en qué tan alta es la onda). Si se suman ambas ondas se obtiene algo como la siguiente onda. Esta, también se puede representar como lo siguiente: en el eje x tenemos frecuencia y en el eje y tenemos o potencia. Se ve que esta onda [la en el tiempo], se compone de dos ondas, una de baja potencia y 4 hz, y la otra de mayor amplitud y 10 hz, que son justamente las ondas que vimos allá.
      Esto es hacer un análisis de frecuencia, descomponer esta onda en las frecuencias que la componen.
      La onda EEG que recibimos, que vimos en la demo, justamente es como esta, es una suma de muchas ondas de distintas frecuencias y distintas potencias. Lo que se quiere es tomar una onda como esta, y descomponerla.
    + fourier transform para obtener freqs
      Para hacer esto existe una herramienta matemática llamada transformación de fourier, que justamente toma una ventana de la onda y nos indica qué frecuencias la componen. Me estoy saltando un par de pasos matemáticos pero esta es la idea principal.
      Lo que se hace entonces es tomar una ventana de tiempo de la onda y aplicar el cálculo para obtener algo así. Luego se mueve la ventana y se vuelve a calcular, y así durante toda la onda en el tiempo, se van acumulando estos gráficos en el tiempo.
    + Mapa calor
      Aplicando esto en toda la onda se obtienen este tipo de gráficos. En el eje x está el tiempo, en el eje y está la frecuencia, y en el eje z (el del color) nos indica la potencia.
      Aquí por ejemplo tenemos que en este ejemplo, en el segundo X hubo un aumento de potencia en las frecuencias más bajas, etc.

  - Ondas
    Las ondas cerebrales las descomponen por su rango de frecuencias, entre 8 y 13 Hz está la onda alpha, etc.
    La gracia de estas ondas es que según estudios están asociadas a distintos estados mentales. Por ejemplo, activación alpha está asociada a que la persona está relajada, la onda delta se activa en el sueño, etc.
    El programa que hice también calcula estas ondas y las manda a la página web. [ver por tiempo si hacer demo o no]

  - opciones mapeo EEG (emoción)
    Ahora teníamos que elegir una forma de pasar la onda anterior, ya sea la onda cruda o las ondas alpha, beta, etc; para mapear esto a un estado mental o a una emoción.
    Tenemos 3 opciones:
      + Mapear directamente al espacio GEMS en el que está moodplay, que fue mostrado anteriormente. Este tiene las emociones ...
      + Vimos en la literatura el espacio de emoción valence-arousal, que muestra ... (cada eje y ejemplos)
      + Relajado-concentrado, simple, vimos en la literatura alpha y beta
      + Cuarta opción: mezcla de varias. Lo que estamos probando en la práctica es mapear de relax-conc a GEMS.

  - relax-conc
    Modelamos esto de la siguiente manera, un eje para cada emoción entre relajado y concentrado.
    Un par de observaciones: los ejes no necesariamente son independientes, quizás si una persona está concentrada implica que no estará tan relajada, o viceversa, pero este es un modelo simplificado.
    No relajado puede ser activo o tenso.
    Tenemos aquí unos ejemplos de artistas, [leer]. Ahora estos son para que tengan una idea, una opción es personalizar esto y descubrir qué le acomoda a cada usuario.

* Muse + moodplay
  El mapeo de lo anterior no es directo al espacio GEMS, pero se puede ver algo como lo siguiente...

* Desafíos
  Como desafíos a resolver a continuación, tenemos varias cosas
  1. Artifact removal, ruido
    Como vieron la onda cruda EEG tiene bastante ruido, por ejemplo parpadeos y otros movimientos del usuario. Cualquier ruido aquí se propaga a los cálculos siguientes. Para remover estos existen técnicas como ICA, pero son usadas mayormente offline. Lo que nosotros estamos haciendo es en tiempo real, por lo que estamos viendo una variación de esto para lograr remover el ruido en tiempo real.

  2. Señal EEG -> dominio relax-conc, GEMS, etc
    Otro desafío que tenemos es el mapeo de la señal EEG que tenemos a un dominio de utilidad, en el caso de moodplay es el dominio GEMS.

  3. Interfaz de usuario + visualización
    Y por último también tenemos que ver cómo mostrar toda esta información con una buena visualización y con una interfaz adecuada para el usuario.

* Anexos
