public class PracticaOrdenamiento {
    public static void main(String[] args) {
        int comparaciones = 0;
        int movimientos = 0;
        int[] arreglo = new int[args.length];

        for (int i = 0; i < args.length; i++) {
            arreglo[i] = Integer.parseInt(args[i]);
        }

        for (int i = 1; i < arreglo.length; i++) {
            int actual = arreglo[i];
            int j = i - 1;

            while (j >= 0) {
                comparaciones++;
                if (arreglo[j] < actual) {
                    break;
                }
                arreglo[j + 1] = arreglo[j];
                movimientos++;
                j--;
            }
            arreglo[j + 1] = actual;
            movimientos++;
        }

        System.out.println("Comparaciones: " + comparaciones);
        System.out.println("Movimientos: " + movimientos);
    }
}