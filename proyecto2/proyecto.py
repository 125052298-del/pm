import numpy as np
import heapq
import matplotlib.pyplot as plt

# ==============================================================================
# PASO 1: Malla ráster de 100 x 100 puntos
# ==============================================================================
N, dx = 100, 10.0  # Nodos por lado, espaciamiento [m]
x = np.arange(N) * dx
y = np.arange(N) * dx
X, Y = np.meshgrid(x, y)

# ==============================================================================
# PASO 2: Modelo Digital de Elevaciones z = f(x,y) (Terreno Único del Equipo)
# ==============================================================================
xc = 500.0
Z1 = 120 + 0.12 * Y
Z2 = 60 * (1 - np.cos(np.pi * (X - xc) / 400.0))
Z3 = 30 * np.exp(-((X - 250)**2 + (Y - 700)**2) / (2 * 85**2)) + 20 * np.exp(-((X - 750)**2 + (Y - 400)**2) / (2 * 95**2))
Z4 = 10 * np.sin(X / 60.0) * np.sin(Y / 80.0)

Z = Z1 + Z2 + Z3 + Z4

# ==============================================================================
# PASO 3: Eliminar depresiones (Priority-Flood)
# ==============================================================================
def rellenar(Z, eps=1e-3):
    n, m = Z.shape
    F = np.full(Z.shape, np.inf)
    visto = np.zeros(Z.shape, bool)
    cola = []
    for i in range(n):
        for j in range(m):
            if i in (0, n - 1) or j in (0, m - 1):
                F[i, j] = Z[i, j]
                visto[i, j] = True
                heapq.heappush(cola, (Z[i, j], i, j))
    while cola:
        z_val, i, j = heapq.heappop(cola)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                a, b = i + di, j + dj
                if (di or dj) and 0 <= a < n and 0 <= b < m and not visto[a, b]:
                    visto[a, b] = True
                    F[a, b] = max(Z[a, b], z_val + eps)
                    heapq.heappush(cola, (F[a, b], a, b))
    return F

Zf = rellenar(Z)

# ==============================================================================
# PASO 4: Gradiente y Pendiente
# ==============================================================================
n, m = Zf.shape
Zy, Zx = np.gradient(Zf, dx)  # Diferencias finitas centrales
S = np.hypot(Zx, Zy)           # Pendiente S = ||grad z||

# ==============================================================================
# PASO 5: Dirección de flujo (D8)
# ==============================================================================
vecinos = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
recep = -np.ones((n, m, 2), int)

for i in range(n):
    for j in range(m):
        mejor = 0.0
        for di, dj in vecinos:
            a, b = i + di, j + dj
            if 0 <= a < n and 0 <= b < m:
                s = (Zf[i, j] - Zf[a, b]) / (dx * np.hypot(di, dj))
                if s > mejor:
                    mejor = s
                    recep[i, j] = (a, b)

# ==============================================================================
# PASO 6: Acumulación de flujo
# ==============================================================================
orden = np.dstack(np.unravel_index(np.argsort(-Zf, axis=None), Zf.shape))[0]
acc = np.ones((n, m))
for i, j in orden:
    a, b = recep[i, j]
    if a >= 0:
        acc[a, b] += acc[i, j]

# ==============================================================================
# PASO 7: Salida, Parteaguas y Área de la cuenca
# ==============================================================================
borde = np.zeros((n, m), bool)
borde[[0, -1], :] = True
borde[:, [0, -1]] = True
io, jo = np.unravel_index(np.where(borde, acc, 0).argmax(), acc.shape)

cuenca = np.zeros((n, m), bool)
for i, j in orden[::-1]:
    if (i, j) == (io, jo):
        cuenca[i, j] = True
    else:
        a, b = recep[i, j]
        if a >= 0 and cuenca[a, b]:
            cuenca[i, j] = True

A_cel = cuenca.sum() * dx * dx
A_sup = np.sqrt(1 + Zx**2 + Zy**2)[cuenca].sum() * dx * dx
A_km2 = A_cel / 1e6

# ==============================================================================
# PASO 8: Red de cauces y cauce principal
# ==============================================================================
U = 100  # Umbral de acumulación [celdas]
cauces = (acc >= U) & cuenca

def donantes(i, j):
    out = []
    for di, dj in vecinos:
        a, b = i + di, j + dj
        if 0 <= a < n and 0 <= b < m and tuple(recep[a, b]) == (i, j):
            out.append((a, b))
    return out

ruta = [(io, jo)]
while True:
    d = [c for c in donantes(*ruta[-1]) if cuenca[c]]
    if not d: break
    sig = max(d, key=lambda c: acc[c])
    if acc[sig] < 20: break
    ruta.append(sig)

ruta = ruta[::-1]
zc = np.array([Zf[c] for c in ruta])
dl = np.array([dx * np.hypot(ruta[k+1][0] - ruta[k][0], ruta[k+1][1] - ruta[k][1]) for k in range(len(ruta)-1)])
sk = (zc[:-1] - zc[1:]) / dl
L = dl.sum()
S_med = (zc[0] - zc[-1]) / L
S_max, S_min = sk.max(), sk.min()

# ==============================================================================
# PASO 9: Tiempo de concentración y gasto racional
# ==============================================================================
tc = 0.0195 * (L**0.77) * (S_med**(-0.385))  # Kirpich [min]
C = 0.5
intensidades = [30, 60, 90, 120]  # [mm/h]
Q = [C * i * A_km2 / 3.6 for i in intensidades]  # [m3/s]

print("=== RESULTADOS DE LA CUENCA DE TU EQUIPO ===")
print(f"Área planimétrica A: {A_km2:.3f} km2 ({cuenca.sum()} celdas)")
print(f"Área superficial A_sup: {A_sup/1e6:.3f} km2")
print(f"Longitud cauce L: {L:.1f} m")
print(f"Desnivel total (z0 - zm): {zc[0] - zc[-1]:.1f} m")
print(f"Pendiente media S_med: {S_med:.4f}")
print(f"Pendientes S_max / S_min: {S_max:.4f} / {S_min:.4f}")
print(f"Tiempo de concentración tc: {tc:.2f} min")
print("-" * 45)
print("GASTO DE PICO Q (MÉTODO RACIONAL, C = 0.5):")
for i_val, q_val in zip(intensidades, Q):
    print(f"  i = {i_val:3d} mm/h  -->  Q = {q_val:6.2f} m3/s")

# ==============================================================================
# PASO 10: Visualización y exportación de las 4 figuras
# ==============================================================================
cx = [X[c] for c in ruta]
cy = [Y[c] for c in ruta]
cz = [Zf[c] + 8 for c in ruta]

# 1. Superficie 3D del DEM (fig_3d.png)
fig = plt.figure(figsize=(7, 5.5))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Zf, cmap='terrain', linewidth=0, antialiased=True, alpha=0.95)
ax.plot(cx, cy, cz, 'r-', lw=2, label='Cauce principal')
ax.set_xlabel('x [m]')
ax.set_ylabel('y [m]')
ax.set_zlabel('z [m]')
ax.view_init(35, -60)
plt.tight_layout()
plt.savefig('fig_3d.png', dpi=200)
plt.close()

# 2. Mapa de contornos con parteaguas y cauces (fig_contornos.png)
fig, ax = plt.subplots(figsize=(7, 5.5))
cs = ax.contourf(X, Y, Zf, 25, cmap='terrain')
ax.contour(X, Y, Zf, 25, colors='k', linewidths=0.3)
plt.colorbar(cs, label='z [m]')
ax.contour(X, Y, cuenca.astype(float), [0.5], colors='k', linewidths=2)
ax.plot(X[cauces], Y[cauces], 'b.', ms=3)
ax.plot(cx, cy, 'r', lw=2)
ax.plot(X[io, jo], Y[io, jo], 'ws', mec='k')
ax.set_aspect('equal')
ax.set_xlabel('x [m]')
ax.set_ylabel('y [m]')
plt.tight_layout()
plt.savefig('fig_contornos.png', dpi=200)
plt.close()

# 3. Mapa de pendiente en grados (fig_pendiente.png)
fig, ax = plt.subplots(figsize=(7, 5.5))
im = ax.imshow(np.degrees(np.arctan(S)), origin='lower', extent=[0, x[-1], 0, y[-1]], cmap='magma')
plt.colorbar(im, label=r'$\theta$ [grados]')
ax.contour(X, Y, cuenca.astype(float), [0.5], colors='c', linewidths=2)
ax.set_xlabel('x [m]')
ax.set_ylabel('y [m]')
plt.tight_layout()
plt.savefig('fig_pendiente.png', dpi=200)
plt.close()

# 4. Perfil longitudinal y gráfica Q vs i (fig_perfil_gasto.png)
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
s_acum = np.concatenate([[0], np.cumsum(dl)])
ax[0].plot(s_acum, zc, 'b-')
ax[0].set_xlabel('Distancia desde la salida [m]')
ax[0].set_ylabel('z [m]')
ax[0].set_title('Perfil longitudinal del cauce principal')

ii = np.linspace(10, 150, 50)
ax[1].plot(ii, C * ii * A_km2 / 3.6, 'r-')
ax[1].set_xlabel('i [mm/h]')
ax[1].set_ylabel('Q [m3/s]')
ax[1].set_title('Gasto (Método Racional)')
plt.tight_layout()
plt.savefig('fig_perfil_gasto.png', dpi=200)
plt.close()

print("\n¡Proceso completado exitosamente! Se guardaron las 4 figuras png en la carpeta actual.")