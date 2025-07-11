# 🎯 Presentación: QuadTree en Snake Game
## Algoritmos y Estructuras de Datos

---

## 1. INTRODUCCIÓN Y PROBLEMÁTICA (2 min)

### El Problema Clásico
En juegos como Snake, detectar colisiones tradicionalmente requiere:

```cpp
// ❌ Método tradicional - O(n)
bool checkCollision(Vec2 newHead, vector<Vec2>& snake) {
    for (auto& segment : snake) {
        if (newHead == segment) {
            return true; // ¡Colisión!
        }
    }
    return false;
}
```

**Problema**: Con una serpiente de 1000 segmentos = 1000 comparaciones **cada movimiento**

### La Solución: QuadTree
```cpp
// ✅ Método optimizado - O(log n)
bool checkCollision(Vec2 newHead, Quadtree& quadtree) {
    return quadtree.search(newHead); // Solo ~10 comparaciones
}
```

**Ventaja**: Independiente del tamaño de la serpiente, siempre logarítmico.

---

## 2. FUNDAMENTOS DEL QUADTREE (4-5 min)

### ¿Qué es un QuadTree?
- **Estructura de datos espacial** que divide el espacio 2D recursivamente
- Cada nodo representa un **área rectangular**
- Cada nodo puede tener **0 o 4 hijos** (nunca 1, 2 o 3)
- Se subdivide cuando supera la **capacidad máxima**

### Visualización del Concepto
```
┌─────────────────┐     ┌─────────┬─────────┐
│        ●        │ →   │    ●    │         │
│      ●   ●      │     ├─────────┼─────────┤
│         ●       │     │   ●     │    ●    │
└─────────────────┘     └─────────┴─────────┘
  Capacidad: 4            Subdividido en 4
```

### Estructura del Nodo
```cpp
class Quadtree {
private:
    // Límites del área que cubre este nodo
    int x, y, width, height;
    
    // Capacidad máxima antes de subdividir
    static const int CAPACITY = 4;
    
    // Puntos almacenados localmente
    std::vector<Vec2> points;
    
    // Los 4 cuadrantes hijos
    std::unique_ptr<Quadtree> topLeft;
    std::unique_ptr<Quadtree> topRight;
    std::unique_ptr<Quadtree> bottomLeft;
    std::unique_ptr<Quadtree> bottomRight;
    
    bool divided; // ¿Ya se subdividió?
};
```

---

## 3. ALGORITMOS PRINCIPALES (6-7 min)

### A. ALGORITMO INSERT - El Corazón del QuadTree

```cpp
bool Quadtree::insert(const Vec2& point) {
    // 1️⃣ Verificar si el punto está dentro de los límites
    if (!contains(point)) {
        return false; // Fuera de rango
    }
    
    // 2️⃣ Si hay espacio y no está dividido, insertar aquí
    if (!divided && points.size() < CAPACITY) {
        points.push_back(point);
        return true;
    }
    
    // 3️⃣ Si necesitamos dividir, hazlo
    if (!divided) {
        subdivide(); // ¡Crea los 4 hijos!
    }
    
    // 4️⃣ Insertar en el cuadrante correcto
    if (topLeft->contains(point)) {
        return topLeft->insert(point);
    } else if (topRight->contains(point)) {
        return topRight->insert(point);
    } else if (bottomLeft->contains(point)) {
        return bottomLeft->insert(point);
    } else if (bottomRight->contains(point)) {
        return bottomRight->insert(point);
    }
    
    return false;
}
```

**Paso a paso**:
1. **Verificar límites**: ¿El punto pertenece a este nodo?
2. **Inserción directa**: Si hay espacio y no está dividido
3. **Subdivisión automática**: Si se supera la capacidad
4. **Delegación recursiva**: Insertar en el hijo apropiado

### B. ALGORITMO SUBDIVIDE - Particionamiento Espacial

```cpp
void Quadtree::subdivide() {
    if (divided) return; // Ya está dividido
    
    int halfWidth = width / 2;
    int halfHeight = height / 2;
    
    // Crear los 4 cuadrantes
    topLeft = std::make_unique<Quadtree>(
        x, y, halfWidth, halfHeight
    );
    topRight = std::make_unique<Quadtree>(
        x + halfWidth, y, halfWidth, halfHeight
    );
    bottomLeft = std::make_unique<Quadtree>(
        x, y + halfHeight, halfWidth, halfHeight
    );
    bottomRight = std::make_unique<Quadtree>(
        x + halfWidth, y + halfHeight, halfWidth, halfHeight
    );
    
    divided = true;
    
    // Redistribuir puntos existentes
    for (const auto& point : points) {
        if (topLeft->contains(point)) {
            topLeft->insert(point);
        } else if (topRight->contains(point)) {
            topRight->insert(point);
        } // ... etc para otros cuadrantes
    }
    
    points.clear(); // Limpiar el nodo padre
}
```

**Lo que sucede**:
1. **División geométrica**: El área se parte en 4 exactamente
2. **Creación de hijos**: 4 nuevos QuadTrees con áreas específicas
3. **Redistribución**: Los puntos locales se mueven a los hijos apropiados
4. **Limpieza**: El nodo padre ya no almacena puntos directamente

### C. ALGORITMO SEARCH - Navegación Inteligente

```cpp
bool Quadtree::search(const Vec2& point) const {
    // 1️⃣ Verificar límites
    if (!contains(point)) {
        return false;
    }
    
    // 2️⃣ Si no está dividido, buscar localmente
    if (!divided) {
        return std::find(points.begin(), points.end(), point) 
               != points.end();
    }
    
    // 3️⃣ Si está dividido, buscar SOLO en el cuadrante correcto
    if (topLeft->contains(point)) {
        return topLeft->search(point);
    } else if (topRight->contains(point)) {
        return topRight->search(point);
    } else if (bottomLeft->contains(point)) {
        return bottomLeft->search(point);
    } else if (bottomRight->contains(point)) {
        return bottomRight->search(point);
    }
    
    return false;
}
```

**La Magia de la Eficiencia**:
- ❌ **NO** busca en los 4 cuadrantes
- ✅ **SOLO** busca en el cuadrante que contiene el punto
- 🎯 Esto reduce la búsqueda de O(n) a O(log n)

---

## 4. INTEGRACIÓN EN EL JUEGO SNAKE (3-4 min)

### El Ciclo de Vida en el Juego

```cpp
void Game::updateGame() {
    // 1️⃣ Calcular próxima posición SIN mover
    Vec2 nextHead = calculateNextPosition();
    
    // 2️⃣ DETECCIÓN DE COLISIÓN con QuadTree
    if (quadtree.search(nextHead)) {
        gameOver = true; // ¡Colisión detectada!
        return;
    }
    
    // 3️⃣ Verificar si va a comer comida
    bool willEat = (nextHead == food.getPosition());
    if (willEat) {
        snake.grow(); // Marcar para crecer
        spawnFood();  // Nueva comida
    }
    
    // 4️⃣ Guardar cola antes del movimiento
    Vec2 oldTail = snake.getTail();
    
    // 5️⃣ Mover la serpiente
    Vec2 newHead = snake.move();
    
    // 6️⃣ ACTUALIZAR QuadTree
    quadtree.insert(newHead);           // Nueva cabeza
    if (snake.shouldRemoveTail()) {
        quadtree.remove(oldTail);       // Quitar cola vieja
    }
}
```

### Generación Inteligente de Comida

```cpp
void Game::spawnFood() {
    Vec2 newFoodPos;
    int attempts = 0;
    
    do {
        newFoodPos = food.generateRandomPosition();
        attempts++;
    } while (quadtree.search(newFoodPos) && attempts < 1000);
    //       ↑ Verificación ultra-rápida con QuadTree
    
    food.setPosition(newFoodPos);
}
```

**Ventaja**: Encontrar posición libre es O(log n) en lugar de generar hasta que no colisione.

---

## 5. ANÁLISIS DE COMPLEJIDAD (2-3 min)

### Comparación Teórica

| Operación | Método Tradicional | Con QuadTree | Mejora |
|-----------|-------------------|--------------|---------|
| **Detección colisión** | O(n) | O(log n) | Logarítmica |
| **Insertar cabeza** | O(1) | O(log n) | Overhead mínimo |
| **Eliminar cola** | O(n) | O(log n) | Logarítmica |
| **Buscar comida libre** | O(n × intentos) | O(log n × intentos) | Logarítmica |

### Escalabilidad Práctica

```
Serpiente de 100 segmentos:
- Tradicional: 100 comparaciones
- QuadTree: ~7 comparaciones (log₄ 100)

Serpiente de 1,000 segmentos:
- Tradicional: 1,000 comparaciones  
- QuadTree: ~10 comparaciones (log₄ 1000)

Serpiente de 10,000 segmentos:
- Tradicional: 10,000 comparaciones
- QuadTree: ~13 comparaciones (log₄ 10000)
```

### ¿Por qué funciona tan bien?
- **Profundidad máxima**: log₄(n) donde n = número de puntos
- **Búsqueda dirigida**: Solo explora el camino necesario
- **Subdivisión automática**: Se adapta dinámicamente al contenido

---

## 6. DEMOSTRACIÓN PRÁCTICA (2-3 min)

### Compilación y Ejecución
```bash
# Compilar el proyecto
mkdir build && cd build
cmake ..
make

# Ejecutar
./main
```

### Operaciones en Tiempo Real
Durante la demostración:

1. **Inicio**: QuadTree contiene serpiente inicial + obstáculos
2. **Movimiento**: Cada tecla → INSERT nueva cabeza + REMOVE cola  
3. **Crecimiento**: Solo INSERT cabeza (cola se mantiene)
4. **Colisión**: SEARCH retorna true → Game Over

### Métricas Observables
- **Velocidad constante**: Independiente del tamaño de serpiente
- **Memoria eficiente**: Solo subdivisión donde hay densidad
- **Respuesta inmediata**: O(log n) es imperceptible al usuario

---

## 7. CONCLUSIONES ACADÉMICAS (1-2 min)

### Logros del Proyecto
✅ **Implementación completa** de QuadTree desde cero  
✅ **Aplicación práctica** en problema de colisiones 2D  
✅ **Análisis empírico** de complejidad algoritmica  
✅ **Código modular** y bien documentado  

### Conceptos Demostrados
- **Estructuras de datos espaciales**
- **Recursión y subdivisión**
- **Análisis de complejidad temporal**
- **Optimización de algoritmos**

### Aplicaciones Futuras
- **Videojuegos**: Detección de colisiones en mundo abierto
- **Simulaciones**: Sistemas de partículas, física
- **GIS**: Sistemas de información geográfica
- **Robótica**: Navegación y mapeo

### Valor Académico
Este proyecto demuestra que **elegir la estructura de datos correcta** puede transformar un algoritmo O(n) en O(log n), haciendo la diferencia entre un sistema escalable y uno que colapsa con el crecimiento.

---

## 📊 Datos Técnicos del Proyecto

- **Lenguaje**: C++17
- **Gráficos**: SFML 2.5+
- **Paradigma**: Programación Orientada a Objetos
- **Líneas de código**: ~1000+
- **Capacidad QuadTree**: 4 puntos por nodo
- **Tablero**: 50×50 = 2,500 posiciones posibles
- **Profundidad máxima teórica**: ~6 niveles

---

*"El QuadTree no solo optimiza el Snake, demuestra cómo las estructuras de datos espaciales resuelven problemas fundamentales en computación 2D"*
