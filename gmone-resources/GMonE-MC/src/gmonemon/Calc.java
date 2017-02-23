/******************************************************************************
 * 
 *  GMonE: A customizable monitoring tool for distributed systems
 *  Copyright (C) 2010  Jesus Montes
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *  
 *****************************************************************************/

// Output created by jacc on Thu May 18 13:34:35 CEST 2006

package gmonemon;

class Calc implements CalcTokens {
    private int yyss = 100;
    private int yytok;
    private int yysp = 0;
    private int[] yyst;
    protected int yyerrno = (-1);
    private double[] yysv;
    private double yyrv;

    public boolean parse() {
        int yyn = 0;
        yysp = 0;
        yyst = new int[yyss];
        yysv = new double[yyss];
        yytok = (token
                 );
    //loop:
        for (;;) {
            switch (yyn) {
                case 0:
                    yyst[yysp] = 0;
                    if (++yysp>=yyst.length) {
                        yyexpand();
                    }
                case 15:
                    switch (yytok) {
                        case DOUBLE:
                            yyn = 3;
                            continue;
                        case '(':
                            yyn = 4;
                            continue;
                    }
                    yyn = 33;
                    continue;

                case 1:
                    yyst[yysp] = 1;
                    if (++yysp>=yyst.length) {
                        yyexpand();
                    }
                case 16:
                    switch (yytok) {
                        case ENDINPUT:
                            yyn = 30;
                            continue;
                    }
                    yyn = 33;
                    continue;

                case 2:
                    yyst[yysp] = 2;
                    if (++yysp>=yyst.length) {
                        yyexpand();
                    }
                case 17:
                    switch (yytok) {
                        case '*':
                            yyn = 5;
                            continue;
                        case '+':
                            yyn = 6;
                            continue;
                        case '-':
                            yyn = 7;
                            continue;
                        case '/':
                            yyn = 8;
                            continue;
                        case ENDINPUT:
                            yyn = yyr1();
                            continue;
                    }
                    yyn = 33;
                    continue;

                case 3:
                    yyst[yysp] = 3;
                    yysv[yysp] = (yylval
                                 );
                    yytok = (yylex()
                            );
                    if (++yysp>=yyst.length) {
                        yyexpand();
                    }
                case 18:
                    switch (yytok) {
                        case INTEGER:
                        case '(':
                        case DOUBLE:
                        case ';':
                        case error:
                            yyn = 33;
                            continue;
                    }
                    yyn = yyr7();
                    continue;

                case 4:
                    yyst[yysp] = 4;
                    yysv[yysp] = (yylval
                                 );
                    yytok = (yylex()
                            );
                    if (++yysp>=yyst.length) {
                        yyexpand();
                    }
                case 19:
                    switch (yytok) {
                        case DOUBLE:
                            yyn = 3;
                            continue;
                        case '(':
                            yyn = 4;
                            continue;
                    }
                    yyn = 33;
                    continue;

                case 5:
                    yyst[yysp] = 5;
                    yysv[yysp] = (yylval
                                 );
                    yytok = (yylex()
                            );
                    if (++yysp>=yyst.length) {
                        yyexpand();
                    }
                case 20:
                    switch (yytok) {
                        case DOUBLE:
                            yyn = 3;
                            continue;
                        case '(':
                            yyn = 4;
                            continue;
                    }
                    yyn = 33;
                    continue;

                case 6:
                    yyst[yysp] = 6;
                    yysv[yysp] = (yylval
                                 );
                    yytok = (yylex()
                            );
                    if (++yysp>=yyst.length) {
                        yyexpand();
                    }
                case 21:
                    switch (yytok) {
                        case DOUBLE:
                            yyn = 3;
                            continue;
                        case '(':
                            yyn = 4;
                            continue;
                    }
                    yyn = 33;
                    continue;

                case 7:
                    yyst[yysp] = 7;
                    yysv[yysp] = (yylval
                                 );
                    yytok = (yylex()
                            );
                    if (++yysp>=yyst.length) {
                        yyexpand();
                    }
                case 22:
                    switch (yytok) {
                        case DOUBLE:
                            yyn = 3;
                            continue;
                        case '(':
                            yyn = 4;
                            continue;
                    }
                    yyn = 33;
                    continue;

                case 8:
                    yyst[yysp] = 8;
                    yysv[yysp] = (yylval
                                 );
                    yytok = (yylex()
                            );
                    if (++yysp>=yyst.length) {
                        yyexpand();
                    }
                case 23:
                    switch (yytok) {
                        case DOUBLE:
                            yyn = 3;
                            continue;
                        case '(':
                            yyn = 4;
                            continue;
                    }
                    yyn = 33;
                    continue;

                case 9:
                    yyst[yysp] = 9;
                    if (++yysp>=yyst.length) {
                        yyexpand();
                    }
                case 24:
                    switch (yytok) {
                        case '*':
                            yyn = 5;
                            continue;
                        case '+':
                            yyn = 6;
                            continue;
                        case '-':
                            yyn = 7;
                            continue;
                        case '/':
                            yyn = 8;
                            continue;
                        case ')':
                            yyn = 14;
                            continue;
                    }
                    yyn = 33;
                    continue;

                case 10:
                    yyst[yysp] = 10;
                    if (++yysp>=yyst.length) {
                        yyexpand();
                    }
                case 25:
                    switch (yytok) {
                        case INTEGER:
                        case '(':
                        case DOUBLE:
                        case ';':
                        case error:
                            yyn = 33;
                            continue;
                    }
                    yyn = yyr4();
                    continue;

                case 11:
                    yyst[yysp] = 11;
                    if (++yysp>=yyst.length) {
                        yyexpand();
                    }
                case 26:
                    yyn = yys11();
                    continue;

                case 12:
                    yyst[yysp] = 12;
                    if (++yysp>=yyst.length) {
                        yyexpand();
                    }
                case 27:
                    yyn = yys12();
                    continue;

                case 13:
                    yyst[yysp] = 13;
                    if (++yysp>=yyst.length) {
                        yyexpand();
                    }
                case 28:
                    switch (yytok) {
                        case INTEGER:
                        case '(':
                        case DOUBLE:
                        case ';':
                        case error:
                            yyn = 33;
                            continue;
                    }
                    yyn = yyr5();
                    continue;

                case 14:
                    yyst[yysp] = 14;
                    yysv[yysp] = (yylval
                                 );
                    yytok = (yylex()
                            );
                    if (++yysp>=yyst.length) {
                        yyexpand();
                    }
                case 29:
                    switch (yytok) {
                        case INTEGER:
                        case '(':
                        case DOUBLE:
                        case ';':
                        case error:
                            yyn = 33;
                            continue;
                    }
                    yyn = yyr6();
                    continue;

                case 30:
                    return true;
                case 31:
                    yyerror("stack overflow");
                case 32:
                    return false;
                case 33:
                    yyerror("syntax error");
                    return false;
            }
        }
    }

    protected void yyexpand() {
        int[] newyyst = new int[2*yyst.length];
        double[] newyysv = new double[2*yyst.length];
        for (int i=0; i<yyst.length; i++) {
            newyyst[i] = yyst[i];
            newyysv[i] = yysv[i];
        }
        yyst = newyyst;
        yysv = newyysv;
    }

    private int yys11() {
        switch (yytok) {
            case '*':
                return 5;
            case '/':
                return 8;
            case '+':
            case ENDINPUT:
            case ')':
            case '-':
                return yyr2();
        }
        return 33;
    }

    private int yys12() {
        switch (yytok) {
            case '*':
                return 5;
            case '/':
                return 8;
            case '+':
            case ENDINPUT:
            case ')':
            case '-':
                return yyr3();
        }
        return 33;
    }

    private int yyr1() { // prog : expr
        { valor = yysv[yysp-1]; }
        yysv[yysp-=1] = yyrv;
        return 1;
    }

    private int yyr2() { // expr : expr '+' expr
        { yyrv = yysv[yysp-3] + yysv[yysp-1]; }
        yysv[yysp-=3] = yyrv;
        return yypexpr();
    }

    private int yyr3() { // expr : expr '-' expr
        { yyrv = yysv[yysp-3] - yysv[yysp-1]; }
        yysv[yysp-=3] = yyrv;
        return yypexpr();
    }

    private int yyr4() { // expr : expr '*' expr
        { yyrv = yysv[yysp-3] * yysv[yysp-1]; }
        yysv[yysp-=3] = yyrv;
        return yypexpr();
    }

    private int yyr5() { // expr : expr '/' expr
        { yyrv = yysv[yysp-3] / yysv[yysp-1]; }
        yysv[yysp-=3] = yyrv;
        return yypexpr();
    }

    private int yyr6() { // expr : '(' expr ')'
        { yyrv = yysv[yysp-2]; }
        yysv[yysp-=3] = yyrv;
        return yypexpr();
    }

    private int yyr7() { // expr : DOUBLE
        { yyrv = yysv[yysp-1]; }
        yysv[yysp-=1] = yyrv;
        return yypexpr();
    }

    private int yypexpr() {
        switch (yyst[yysp-1]) {
            case 7: return 12;
            case 6: return 11;
            case 5: return 10;
            case 4: return 9;
            case 0: return 2;
            default: return 13;
        }
    }

    protected String[] yyerrmsgs = {
    };


  public static double valor;
  public static String cadena;
  public static int pos;

  private void yyerror(String msg) {
    System.out.println("ERROR: " + msg);
    //System.exit(1);
  }

  private int c;

  /** Read a single input character from standard input.
   */
  /*
  private void nextChar() {
    if (c>=0) {
      try {
        c = System.in.read();
      } catch (Exception e) {
        c = (-1);
      }
    }
  }
  */

  private void nextChar() {
    if (c>=0) {
      if (pos >= cadena.length())
        c = -1;
      else
        c = cadena.charAt(pos);
        pos++;
    }
  }

  int token;
  double yylval;

  /** Read the next token and return the
   *  corresponding integer code.
   */
  int yylex() {
    for (;;) {
      // Skip whitespace
      while (c==' ' || c=='\n' || c=='\t' || c=='\r') {
        nextChar();
      }
      if (c<0) {
        return (token=ENDINPUT);
      }
      switch (c) {
        case '+' : nextChar();
                   return token='+';
        case '-' : nextChar();
                   return token='-';
        case '*' : nextChar();
                   return token='*';
        case '/' : nextChar();
                   return token='/';
        case '(' : nextChar();
                   return token='(';
        case ')' : nextChar();
                   return token=')';
        case ';' : nextChar();
                   return token=';';
        default  : if (Character.isDigit((char)c)) {
                     double n = 0.0;
                    
                     do {
                         n = 10.0*n + (double)(c - '0');
                         nextChar();
                     } while (Character.isDigit((char)c));
                      double decimal;
                     double i=10.0;
                     if ((char)c =='.'){
                       nextChar();
                       do {
                         decimal= ((double)(c - '0'))/i;
                         i =i*10.0;
                         n = n + decimal;
                         //System.out.println("El valor del numero leido es: "+n);
                         nextChar();
                       } while (Character.isDigit((char)c));
                     }
                     
                       yylval = n;
                       //return token=INTEGER;
                       return token=DOUBLE;
                   } else {
                       yyerror("Illegal character "+c);
                       nextChar();
                   }
      }
    }
  }

  public static double resolver(String arg) {

    cadena = arg;
    pos = 0;

    Calc calc = new Calc();
    calc.nextChar(); // prime the character input stream
    calc.yylex();    // prime the token input stream
    calc.parse();    // parse the input
    return valor;
  }

  public static void main(String[] args) {
    Calc calc = new Calc();
    calc.nextChar(); // prime the character input stream
    calc.yylex();    // prime the token input stream
    calc.parse();    // parse the input
  }

}
