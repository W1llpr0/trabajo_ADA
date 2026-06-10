![](_page_0_Picture_1.jpeg)

# **TRABAJO DE INVESTIGACIÓN**

# **Algoritmos metaheurísticos y el problema PFSP (Permutation Flow Shop Scheduling Problem)**

Para este proyecto, cada grupo deberá investigar, adaptar, implementar y evaluar un algoritmo metaheurístico para resolver el Permutation Flow Shop Scheduling Problem (PFSP).

El PFSP es un problema clásico de optimización combinatoria en el que se debe determinar el mejor orden de procesamiento de un conjunto de trabajos que pasan por una misma secuencia de máquinas. El objetivo será encontrar una secuencia de trabajos que permita minimizar el makespan, es decir, el tiempo total necesario para completar todos los trabajos en todas las máquinas.

## **1. Indicaciones generales**

- La actividad se desarrollará en **grupos de 4 integrantes**.
- Cada grupo trabajará con un algoritmo diferente, pero todos resolverán el mismo tipo de problema, usarán la misma forma de representar las soluciones y deberán reportar sus resultados de acuerdo a las indicaciones detalladas más adelante.
- El algoritmo asignado a su grupo debe ser implementado en el **lenguaje de programación C++**.
- La entrega incluye:
  - **Informe técnico** en Word (máximo de 10 páginas, excluyendo carátula, bibliografía y anexos).
  - **Diapositivas** para su exposición.
  - **Código fuente** de su implementación.
  - **Video** corto del funcionamiento de su implementación, con una duración máxima de 5 mins.
- La fecha de entrega es: **30 / 06 / 2026 a las 23:59pm**
- La fecha de inicio de las exposiciones es: **01 / 07 / 2026**

## **2. Asignación de temas por grupo**

| Grupo | Algoritmo metaheurístico                                   |
|-------|------------------------------------------------------------|
| G4    | Algoritmo de los Fuegos Artificiales (Fireworks Algorithm) |
| G8    | Recocido Simulado (Simulated Annealing, SA)                |
| G1    | Algoritmo Genético (Genetic Algorithm, GA)                 |
| G5    | Colonia de Hormigas (Ant Colony Optimization)              |
| G2    | Enjambre de Partículas (Particle Swarm Optimization)       |
| G7    | Búsqueda Armónica (Harmony Search)                         |
| G6    | Colonia de Abejas Artificiales (Artificial Bee Colony)     |
| G3    | Algoritmo de murciélago (Bat Algorithm)                    |

![](_page_1_Picture_1.jpeg)

## **3. Problema a resolver**

## **3.1. Descripción del problema a resolver**

Una empresa debe procesar un conjunto de trabajos en varias máquinas. Cada trabajo pasa por todas las máquinas siguiendo una misma secuencia de procesamiento. Por ejemplo, si se tienen cuatro máquinas, el recorrido de cada trabajo será:

$$M1 \to M2 \to M3 \to M4$$

Cada trabajo requiere un tiempo específico de procesamiento en cada máquina. Estos tiempos pueden representarse mediante una matriz como la siguiente:

| Trabajo | M1 | M2 | M3 | M4 |
|---------|----|----|----|----|
| J1      | 5  | 8  | 6  | 7  |
| J2      | 4  | 6  | 7  | 5  |
| J3      | 9  | 5  | 8  | 6  |
| J4      | 6  | 7  | 5  | 8  |
| J5      | 7  | 4  | 6  | 9  |

En esta matriz, cada fila representa un trabajo y cada columna representa una máquina. Por ejemplo, el trabajo J1 requiere 5 unidades de tiempo en la máquina M1, 8 en M2, 6 en M3 y 7 en M4.

El problema consiste en determinar el orden en que deben procesarse los trabajos para que el tiempo total de finalización sea el menor posible. En este proyecto se trabajará con el Permutation Flow Shop Scheduling Problem (PFSP), por lo que una solución estará representada por una única permutación de trabajos que se mantiene igual en todas las máquinas.

Por ejemplo, si una posible solución es:

[J3, J1, J4, J2, J5]

entonces esa misma secuencia será utilizada en cada máquina:

Máquina 1: J3 
$$\rightarrow$$
 J1  $\rightarrow$  J4  $\rightarrow$  J2  $\rightarrow$  J5  
Máquina 2: J3  $\rightarrow$  J1  $\rightarrow$  J4  $\rightarrow$  J2  $\rightarrow$  J5  
Máquina 3: J3  $\rightarrow$  J1  $\rightarrow$  J4  $\rightarrow$  J2  $\rightarrow$  J5  
Máquina 4: J3  $\rightarrow$  J1  $\rightarrow$  J4  $\rightarrow$  J2  $\rightarrow$  J5

El objetivo del proyecto es implementar una metaheurística que permita encontrar una secuencia de trabajos que minimice el **makespan**, es decir, el tiempo en que finaliza el último trabajo en la última máquina. En consecuencia, el algoritmo deberá explorar diferentes permutaciones y seleccionar aquella que produzca el menor tiempo total de procesamiento.

#### **3.2. Representación obligatoria de una solución**

Toda solución deberá representarse como una **permutación de trabajos**. Por ejemplo:

[J2, J5, J1, J3, J4]

![](_page_2_Picture_1.jpeg)

Esta secuencia indica el orden en que los trabajos serán procesados en todas las máquinas.

#### **3.3. Cálculo del makespan**

Para evaluar una solución del PFSP, se debe construir una tabla de tiempos de finalización. Esta tabla permite determinar en qué momento termina cada trabajo en cada máquina, considerando las restricciones propias del problema.

El cálculo debe respetar dos condiciones principales:

- 1. Un trabajo solo puede pasar a la siguiente máquina cuando haya terminado su procesamiento en la máquina anterior.
- 2. Una máquina solo puede procesar un trabajo a la vez.

Para cada posición de la secuencia y para cada máquina, el tiempo de finalización se calcula mediante la siguiente expresión:

$$C[i][j] = max(C[i-1][j], C[i][j-1]) + p[i][j]$$

## Donde:

- C[i][j] : Tiempo de finalización del trabajo ubicado en la posición i de la secuencia en la máquina j.
- C[i-1][j] : Tiempo en que la máquina j queda disponible después de procesar el trabajo anterior.
- C[i][j-1] : Tiempo en que el trabajo actual finaliza en la máquina anterior.
- p[i][j]: Tiempo de procesamiento del trabajo ubicado en la posición i en la máquina j.

La función max(C[i-1][j], C[i][j-1]) asegura que el trabajo actual inicie únicamente cuando se cumplan ambas condiciones: que la máquina esté libre y que el trabajo haya terminado en la máquina previa. Luego, se suma el tiempo de procesamiento correspondiente.

**Finalmente, el makespan se obtiene del último valor de la tabla de finalización.** Este valor representa el momento en que termina el último trabajo en la última máquina y será la medida utilizada para evaluar la calidad de cada solución. Mientras menor sea el makespan, mejor será la secuencia de trabajos encontrada.

## **4. Implementación del algoritmo**

El programa deberá permitir cargar una matriz de tiempos de procesamiento desde el archivo **.txt** especificado. A partir de estos datos, deberá generar soluciones iniciales, calcular el makespan de una secuencia de trabajos y ejecutar el algoritmo correspondiente para buscar una mejor solución.

Como resultado de la ejecución, el programa deberá mostrar la mejor secuencia de trabajos encontrada y el mejor makespan obtenido. Además, deberá registrar la evolución del algoritmo durante las iteraciones, de manera que posteriormente se pueda construir la curva de convergencia. También deberá generar o almacenar la información necesaria para elaborar el diagrama de Gantt de la mejor solución.

El código fuente debe entregarse completo y debe cumplir con las siguientes condiciones:

- estar desarrollado en C++;
- estar organizado en funciones, clases o módulos según vea por conveniente;
- incluir comentarios que expliquen las partes principales del algoritmo;
- permitir la carga del archivo de entrada indicado;
- mostrar claramente los resultados obtenidos;
- ser funcional, de manera que debe permitir reproducir los resultados presentados en el informe.

![](_page_3_Picture_1.jpeg)

La implementación será evaluada no solo por el resultado obtenido, sino también por la claridad del código, la correcta adaptación de la metaheurística al PFSP y la posibilidad de verificar experimentalmente los resultados reportados.

## **5. Pruebas y resultados**

#### **5.1. Pruebas experimentales**

El algoritmo deberá evaluarse usando las tres instancias del problema:

| Instancia         | Tamaño sugerido          | Archivo              |
|-------------------|--------------------------|----------------------|
| Instancia pequeña | 5 trabajos × 4 máquinas  | instancia1_bas1.txt  |
| Instancia mediana | 10 trabajos × 6 máquinas | instancia2_car5.txt  |
| Instancia grande  | 20 trabajos × 5 máquinas | instancia3_reC01.txt |

Se recomienda realizar **al menos 10 ejecuciones por instancia**. En cada ejecución se deberá registrar la siguiente información:

- mejor secuencia encontrada;
- makespan obtenido;
- tiempo de ejecución;
- número de iteraciones;
- parámetros utilizados.

Estos datos permitirán analizar la estabilidad del algoritmo y comparar su desempeño en instancias de distinta dificultad.

#### **5.2. Tabla resumen de resultados**

A partir de las ejecuciones realizadas, deberá elaborar una tabla resumen que consolide los principales resultados obtenidos por cada instancia. La tabla debe incluir:

- mejor makespan obtenido;
- peor makespan obtenido;
- makespan promedio;
- desviación estándar;
- tiempo promedio de ejecución;
- mejor secuencia.

Se sugiere usar el siguiente formato:

| Instancia | Mejor<br>makespan | Peor<br>makespan | Promedio | Desviación<br>estándar | Tiempo<br>promedio | Mejor<br>secuencia |
|-----------|-------------------|------------------|----------|------------------------|--------------------|--------------------|
| Pequeña   |                   |                  |          |                        |                    |                    |
| Mediana   |                   |                  |          |                        |                    |                    |

![](_page_4_Picture_1.jpeg)

| Grande |  |  |  |
|--------|--|--|--|
|        |  |  |  |
|        |  |  |  |

Además de la tabla, explicar brevemente qué comportamiento se observa en los resultados. Por ejemplo, pueden analizar si el algoritmo mejora de forma constante, si presenta mucha variabilidad entre ejecuciones, si requiere más tiempo en instancias grandes o si sus resultados dependen significativamente de ciertos parámetros.

#### **5.3. Curva de convergencia**

Debe incluir al menos una curva de convergencia por instancia, que muestre la evolución del algoritmo durante las iteraciones. La gráfica debe representar cómo cambia el mejor makespan encontrado conforme avanza la ejecución del algoritmo. Esta curva permitirá observar si la metaheurística mejora rápidamente al inicio, si se estabiliza después de cierto número de iteraciones o si continúa encontrando mejores soluciones de forma progresiva.

La curva de convergencia debe incluir, como mínimo:

- eje horizontal: número de iteraciones;
- eje vertical: mejor makespan encontrado;
- título de la gráfica.

#### **5.4. Diagrama de Gantt**

Se debe presentar un diagrama de Gantt correspondiente a la mejor secuencia encontrada. Este diagrama debe permitir visualizar cómo se organiza el cronograma generado por el algoritmo.

El diagrama debe mostrar:

- las máquinas consideradas;
- los trabajos procesados en cada máquina;
- los tiempos de inicio de cada operación;
- los tiempos de finalización de cada operación;
- el makespan final.

El diagrama de Gantt puede ser generado directamente por el programa o construido a partir de los tiempos obtenidos durante la evaluación de la mejor solución. En ambos casos, debe ser claro, legible y coherente con el makespan reportado en los resultados.

## **6. Estructura del informe técnico**

- **1. Introducción:** En esta sección se presenta el contexto general del proyecto, explicando la importancia de los problemas de secuenciamiento en la optimización. También se debe mencionar el objetivo del trabajo, el algoritmo asignado al grupo y su aplicación al PFSP.
- **2. Descripción del algoritmo:** Se presenta el algoritmo metaheurístico asignado al grupo, explicando su origen, funcionamiento general y principales componentes. También se deben mencionar sus parámetros más importantes, ventajas, limitaciones y aplicaciones en problemas de optimización.
- **3. Descripción del problema PFSP:** Se explica en qué consiste el Permutation Flow Shop Scheduling Problem, indicando que los trabajos pasan por las máquinas en el mismo orden. Además, se debe describir cómo una solución se representa mediante una permutación de trabajos y que el objetivo es minimizar el makespan.

![](_page_5_Picture_1.jpeg)

- **4. Adaptación del algoritmo al PFSP:** En esta sección se explica cómo el algoritmo fue adaptado para resolver el PFSP. Se debe describir la representación de las soluciones, la generación de soluciones iniciales, los operadores usados sobre permutaciones, la evaluación mediante el makespan y el criterio de parada.
- **5. Pseudocódigo del algoritmo:** Se debe presentar el pseudocódigo del algoritmo adaptado, mostrando de forma ordenada sus pasos principales. Debe incluir la generación de soluciones, evaluación, actualización de la mejor solución y finalización del proceso.
- **6. Descripción de la implementación:** Se describe cómo fue desarrollado el programa en C++, indicando la estructura general del código y las funciones principales. También se debe explicar cómo se cargan los archivos de entrada, cómo se calcula el makespan y cómo se generan los resultados.
- **7. Experimentación:** Se presentan las instancias utilizadas para probar el algoritmo, indicando su tamaño y características. Además, se debe señalar la cantidad de ejecuciones realizadas, los parámetros utilizados y las condiciones bajo las cuales se desarrollaron las pruebas.
- **8. Resultados:** Se muestran los resultados obtenidos en las pruebas experimentales mediante tablas y gráficos. Esta sección debe incluir el mejor makespan, peor makespan, promedio, desviación estándar, tiempo de ejecución, mejor secuencia, curva de convergencia y diagrama de Gantt.
- **9. Análisis y discusión:** Se interpretan los resultados obtenidos, explicando el comportamiento del algoritmo en las diferentes instancias. El análisis debe considerar la calidad de las soluciones, la estabilidad entre ejecuciones, la influencia de los parámetros y la relación entre tiempo de ejecución y resultado obtenido.
- **10. Conclusiones:** Se resumen los principales hallazgos del proyecto, destacando el desempeño del algoritmo aplicado al PFSP. También se deben mencionar las dificultades encontradas, las limitaciones del enfoque y posibles mejoras para trabajos futuros.
- **11. Aportes:** Se debe indicar la contribución específica de cada integrante, evitando descripciones generales como "apoyó en todo" o "participó en el trabajo". Los aportes deben ser claros, específicos y reflejar la participación real de cada estudiante en las diferentes actividades del proyecto. Por ejemplo: *Alumno X: Realizó la implementación y discusión de los resultados de la instancia pequeña. En el reporte colaboró con la redacción de la sección de Introducción y Experimentación.*
- **12. Referencias:** Se incluyen las fuentes bibliográficas utilizadas para sustentar la explicación del algoritmo, el problema PFSP y los conceptos relacionados. Las referencias deben presentarse de manera ordenada y en formato APA.
- **13. Anexos:** Es opcional y puede incluir material complementario que ayude a sustentar el proyecto. Por ejemplo, resultados completos de ejecuciones, capturas del programa, fragmentos de código o tablas adicionales.

## **7. Presentación oral**

Cada grupo deberá realizar una exposición oral en la que presente de manera clara y ordenada el desarrollo de su proyecto. La presentación debe evidenciar que el grupo comprende el problema PFSP, el funcionamiento del algoritmo asignado y la forma en que este fue adaptado para resolver el problema.

![](_page_6_Picture_1.jpeg)

La exposición debe incluir una explicación breve del PFSP, la descripción del algoritmo asignado, la adaptación realizada, el pseudocódigo o flujo general de la solución, los resultados obtenidos, la comparación con una heurística base, el diagrama de Gantt de la mejor solución y las conclusiones principales del trabajo.

**Todos los integrantes del grupo deberán participar en la exposición.** La intervención de cada estudiante debe estar relacionada con una parte relevante del proyecto, de modo que se pueda evidenciar su dominio sobre el trabajo desarrollado.

#### **8. Rúbricas de evaluación**

La evaluación del proyecto se divide en dos componentes: evaluación grupal y evaluación individual. La nota final del proyecto se calculará de la siguiente manera:

#### **Nota final = (Nota grupal × 0.30) + (Nota individual × 0.70)**

#### **Nota Grupal**

| Criterio         | Descripción                                                                                | Pts |
|------------------|--------------------------------------------------------------------------------------------|-----|
| Informe técnico  | Presenta de forma clara, ordenada y completa el algoritmo asignado, el                     | 4   |
|                  | problema<br>abordado,<br>la<br>adaptación realizada,<br>la implementación,<br>las          |     |
|                  | pruebas, los resultados, el análisis y las conclusiones. Incluye redacción                 |     |
|                  | adecuada, estructura coherente y referencias pertinentes.                                  |     |
| Adaptación del   | Explica y justifica correctamente cómo el algoritmo asignado fue aplicado o                | 4   |
| algoritmo al     | adaptado al<br>problema<br>seleccionado.<br>Considera la representación de                 |     |
| problema         | soluciones, función objetivo, generación de nuevas soluciones, criterios de                |     |
|                  | evaluación, parámetros y criterio de parada.                                               |     |
| Código fuente e  | Presenta un código funcional, organizado, comentado y alineado con el                      | 4   |
| implementación   | algoritmo propuesto.<br>Permite cargar o definir los datos de entrada,                     |     |
|                  | ejecutar<br>el<br>algoritmo,<br>obtener<br>resultados<br>y<br>reproducir<br>las<br>pruebas |     |
|                  | presentadas en el informe.                                                                 |     |
| Pruebas          | Ejecuta el algoritmo bajo condiciones definidas, registra resultados de                    | 4   |
| experimentales y | forma<br>ordenada<br>y<br>presenta<br>métricas<br>relevantes<br>para<br>evaluar<br>su      |     |
| resultados       | desempeño, como mejor resultado, peor resultado, promedio, desviación                      |     |
|                  | estándar, tiempo de ejecución u otras según el problema abordado.                          |     |
| Video de         | Demuestra el funcionamiento correcto del programa, evidenciando la                         | 2   |
| funcionamiento   | carga de datos,<br>ejecución del<br>algoritmo,<br>obtención de resultados y                |     |
|                  | coherencia con lo reportado en el informe.                                                 |     |
| Presentación     | Las diapositivas son claras, organizadas, visualmente adecuadas y útiles                   | 2   |
|                  | para apoyar la exposición del proyecto. Presentan de manera sintética el                   |     |
|                  | problema,<br>el<br>algoritmo,<br>la<br>implementación,<br>los<br>resultados<br>y<br>las    |     |
|                  | conclusiones.                                                                              |     |
|                  | TOTAL                                                                                      | 20  |

![](_page_7_Picture_1.jpeg)

| Criterio          | Descripción                                                                              | Pts |
|-------------------|------------------------------------------------------------------------------------------|-----|
| Explicación de la | Explica con claridad, orden y seguridad la sección del proyecto que le                   | 6   |
| parte asignada    | corresponde. Su intervención es fluida, pertinente, respeta los tiempos                  |     |
|                   | asignados y contribuye al desarrollo organizado de la presentación grupal.               |     |
| Claridad y uso de | Utiliza un lenguaje técnico adecuado, comunica sus ideas con precisión y                 | 2   |
| lenguaje técnico  | mantiene seguridad al explicar los conceptos relacionados con el proyecto.               |     |
| Dominio técnico   | Responde correctamente la pregunta individual formulada por el docente,                  | 7   |
| y respuesta a la  | demostrando dominio del<br>algoritmo,<br>del<br>problema abordado,<br>de la              |     |
| pregunta          | implementación,<br>de<br>los<br>parámetros<br>utilizados<br>y<br>de<br>los<br>resultados |     |
| individual        | obtenidos.                                                                               |     |
| Aporte individual | Presenta de forma clara, específica y coherente su contribución realizada                | 3   |
| (informe)         | en<br>la<br>investigación,<br>diseño,<br>implementación,<br>pruebas,<br>análisis<br>o    |     |
|                   | preparación de la exposición, según lo declarado en la sección Aportes del               |     |
|                   | informe técnico.                                                                         |     |
| Coevaluación      | Recibe<br>una<br>valoración<br>positiva<br>de<br>sus<br>compañeros<br>respecto a<br>su   | 2   |
| entre pares       | compromiso, responsabilidad, comunicación y aporte al trabajo grupal.                    |     |
|                   | TOTAL                                                                                    | 20  |