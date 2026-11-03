class CPractica1b {

    // Método que imprime en pantalla una matriz de enteros
    static void imprimir(int[][] m) {
        for(int i=0; i<m.length; i++) {
            for(int j=0; j<m[i].length; j++) {
                System.out.print(m[i][j] + " ") ;
            }
            System.out.println();
        }
        System.out.println("-----------");
    }

    // Método que suma la diagonal invertida ( \ ) de una matriz. Suponga que siempre llegará
    // una matriz cuadrada. Note que el tipo de retorno del método es un entero.
    static int sumarDiagonalInv(int[][] m) {
        int suma = 0;
        for(int i=0; i<m.length; i++) {
            suma += m[i][i];
        }
        return suma;
    }

    // Método que suma la diagonal normal ( / ) de una matriz. Suponga que siempre llegará
    // una matriz cuadrada. Note que el tipo de retorno del método es un entero.
    static int sumarDiagonalNormal(int[][] m) {
        int suma = 0;
        int aux = m.length-1;

        for (int j = m.length-1; j >= 0; j--) {
            suma += m[aux - j][j];
        }

        return suma;
    }

    static int factorial(int n) {
        if (n == 0)
            return 1;
        else
            return n * factorial(n - 1);
    }

    static int fibonacci(int n) {
        if (n == 0)
            return 0;
        else if (n == 1)
                return 1;
             else
                return fibonacci(n-1) + fibonacci(n-2);
    }    

    // Método recursivo que eleva un número b a una potencia e
    static int potencia(int b, int e) {
        if (e == 0)
            return 1;
        else
            return b * potencia(b, e - 1);
    }

    static int bunnyEars(int bunnies) {
        if (bunnies == 0)
            return 0;
        else
            return 2 + bunnyEars(bunnies - 1);
    }

    static boolean array6(int[] nums, int index) {
        if (nums.length == index)
            return false;
        else if (nums[index] == 6)
                return true;
            else 
                return array6(nums, index + 1);
    }    

    public static void main(String args[]) {
        // A continuación se declara e inicializa una matriz de 4 x 4. No borrar
        int[][] mat = {{4,7,8,6}, {3,6,1,2},{6,0,5,7},{9,1,3,4}};
        // Mandamos a imprimir la matriz previamente definida
        imprimir(mat);
        // Sumamos la diagonal invertida de la matriz previamente definida.
        System.out.println("sumaDiagInvertida: " + sumarDiagonalInv(mat));
        // Para que funcionen las siguientes líneas tiene que terminar de 
        // codificar los métodos pendientes antes del main.
        System.out.println("sumaDiagNormal: " + sumarDiagonalNormal(mat));
        System.out.println("factorial: " + factorial(6));
        System.out.println("fibonancci: " + fibonacci(7));
        System.out.println("potencia: " + potencia(2, 6));
        System.out.println("bunnyEars: " + bunnyEars(5));

        int a[] = {1,9,4,6,5};
        System.out.println("array6: " + array6(a,0));
    }
}