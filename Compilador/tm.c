/****************************************************/
/* File: tm.c                                       */
/* The TM ("Tiny Machine") computer                 */
/* Compiler Construction: Principles and Practice   */
/* Kenneth C. Louden                                */
/****************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>

#ifndef TRUE
#define TRUE 1
#endif
#ifndef FALSE
#define FALSE 0
#endif

/******* const *******/
#define IADDR_SIZE 1024 /* increase for large programs */
#define DADDR_SIZE 1024 /* increase for large programs */
#define NO_REGS 8
#define PC_REG 7

#define LINESIZE 121
#define WORDSIZE 20

/******* type  *******/

typedef enum
{
  opclRR, /* reg operands r,s,t */
  opclRM, /* reg r, mem d+s */
  opclRA  /* reg r, int d+s */
} OPCLASS;

typedef enum
{
  /* RR instructions */
  opHALT, /* 0 */
  opIN,   /* 1 */
  opOUT,  /* 2 */
  opADD,  /* 3 */
  opSUB,  /* 4 */
  opMUL,  /* 5 */
  opDIV,  /* 6 */
  opDVF,  /* 7 */
  opLES,  /* 8 */
  opGE,   /* 9 */
  opLEQ,  /* 10 */
  opGEQ,  /* 11 */
  opEQU,  /* 12 */
  opNEQ,  /* 13 */
  opAND,  /* 14 */
  opOR,   /* 15 */
  opNEG,  /* 16 */
  opMIN,  /* 17 */
  opITF,  /* 18 */
  /* RM instructions */
  opLD, /* 19 */
  opST, /* 20 */
  /* RA instructions */
  opLDA, /* 21 */
  opLDC, /* 22 */
  opLDF, /* 23 */
  opJLT, /* 24 */
  opJLE, /* 25 */
  opJGT, /* 26 */
  opJGE, /* 27 */
  opJEQ, /* 28 */
  opJNE, /* 29 */
  opJUC  /* 30 */
} OPCODE;

typedef enum
{
  srOKAY,
  srHALT,
  srIMEM_ERR,
  srDMEM_ERR,
  srZERODIVIDE
} STEPRESULT;

typedef struct
{
  int iop;
  float iarg1;
  float iarg2;
  float iarg3;
} INSTRUCTION;

typedef struct
{
  int isFloat; // 0: entero, 1: flotante
  union
  {
    int iVal;
    float fVal;
  } value;
} REGISTER;

/******** vars ********/
int iloc = 0;
int dloc = 0;
int traceflag = FALSE;
int icountflag = FALSE;

INSTRUCTION iMem[IADDR_SIZE];
REGISTER dMem[DADDR_SIZE];
REGISTER reg[NO_REGS];

const char *opCodeTab[] = {
    /* RR instructions */
    "HALT", "IN", "OUT", "ADD", "SUB", "MUL", "DIV", "DVF", "LES", "GE",
    "LEQ", "GEQ", "EQU", "NEQ", "AND", "OR", "NEG", "MIN", "ITF",
    /* RM instructions */
    "LD", "ST",
    /* RA instructions */
    "LDA", "LDC", "LDF", "JLT", "JLE", "JGT", "JGE", "JEQ", "JNE", "JUC"};

const char *stepResultTab[] = {"OK", "Halted", "Instruction Memory Fault",
                               "Data Memory Fault", "Division by 0"};

char pgmName[20];
FILE *pgm;

char in_Line[LINESIZE];
int lineLen;
int inCol;
float num;
char word[WORDSIZE];
char ch;
int done;

/********************************************/
OPCLASS opClass(int c)
{
  if (c >= opHALT && c <= opITF)
    return opclRR;
  else if (c >= opLD && c <= opST)
    return opclRM;
  else
    return opclRA;
} /* opClass */

/********************************************/
void writeInstruction(int loc)
{
  printf("%5d: ", loc);
  if ((loc >= 0) && (loc < IADDR_SIZE))
  {
    printf("%6s %.0f,", opCodeTab[iMem[loc].iop], iMem[loc].iarg1);
    switch (opClass(iMem[loc].iop))
    {
    case opclRR:
      printf("%.1f,%.1f", iMem[loc].iarg2, iMem[loc].iarg3);
      break;
    case opclRM:
    case opclRA:
      printf("%.1f(%.1f)", iMem[loc].iarg2, iMem[loc].iarg3);
      break;
    }
    printf("\n");
  }
} /* writeInstruction */

/********************************************/
void getCh(void)
{
  if (++inCol < lineLen)
    ch = in_Line[inCol];
  else
    ch = ' ';
} /* getCh */

/********************************************/
int nonBlank(void)
{
  while ((inCol < lineLen) && (in_Line[inCol] == ' '))
    inCol++;
  if (inCol < lineLen)
  {
    ch = in_Line[inCol];
    return TRUE;
  }
  else
  {
    ch = ' ';
    return FALSE;
  }
} /* nonBlank */

/********************************************/
int getNum(void)
{
  int sign = 1;
  int temp = FALSE;
  num = 0;                   // Usado para enteros
  float floatNum = 0.0;      // Usado para flotantes
  int hasDecimal = FALSE;    // Indica si es un número flotante
  double decimalPlace = 0.1; // Para procesar dígitos después del punto decimal

  while (nonBlank() && (ch == '+' || ch == '-')) // Manejo de signos
  {
    temp = FALSE;
    if (ch == '-')
      sign = -sign;
    getCh();
  }

  nonBlank();

  // Procesar la parte entera
  while (isdigit(ch))
  {
    temp = TRUE;
    num = num * 10 + (ch - '0');           // Construir entero
    floatNum = floatNum * 10 + (ch - '0'); // También construir como flotante
    getCh();
  }

  // Verificar si hay un punto decimal
  if (ch == '.')
  {
    hasDecimal = TRUE; // Es un número flotante
    getCh();

    // Procesar la parte decimal
    while (isdigit(ch))
    {
      temp = TRUE;
      floatNum += (ch - '0') * decimalPlace; // Construir flotante
      decimalPlace /= 10;
      getCh();
    }
  }

  // Aplicar signo
  num = num * sign;
  floatNum = floatNum * sign;

  // Si es flotante, usa num como entero convertido
  if (hasDecimal)
  {
    num = floatNum;
  }

  return temp;
} /*Get num */

/********************************************/
int getWord(void)
{
  int temp = FALSE;
  int length = 0;
  if (nonBlank())
  {
    while (isalnum(ch))
    {
      if (length < WORDSIZE - 1)
        word[length++] = ch;
      getCh();
    }
    word[length] = '\0';
    temp = (length != 0);
  }
  return temp;
} /* getWord */

/********************************************/
int skipCh(char c)
{
  int temp = FALSE;
  if (nonBlank() && (ch == c))
  {
    getCh();
    temp = TRUE;
  }
  return temp;
} /* skipCh */

/********************************************/
int atEOL(void)
{
  return (!nonBlank());
} /* atEOL */

/********************************************/
int error(const char *msg, int lineNo, int instNo)
{
  printf("Line %d", lineNo);
  if (instNo >= 0)
    printf(" (Instruction %d)", instNo);
  printf("   %s\n", msg);
  return FALSE;
} /* error */

/********************************************/
int readInstructions(void)
{
  OPCODE op;
  float arg1, arg2, arg3;
  int loc, regNo, lineNo;
  for (regNo = 0; regNo < NO_REGS; regNo++)
  {
    reg[regNo].isFloat = 0;
    reg[regNo].value.iVal = 0;
  }
  dMem[0].isFloat = 0;
  dMem[0].value.iVal = DADDR_SIZE - 1;
  for (loc = 1; loc < DADDR_SIZE; loc++)
  {
    dMem[loc].isFloat = 0;
    dMem[loc].value.iVal = 0;
  }
  for (loc = 0; loc < IADDR_SIZE; loc++)
  {
    iMem[loc].iop = opHALT;
    iMem[loc].iarg1 = 0;
    iMem[loc].iarg2 = 0;
    iMem[loc].iarg3 = 0;
  }
  lineNo = 0;
  while (!feof(pgm))
  {
    fgets(in_Line, LINESIZE - 2, pgm);
    inCol = 0;
    lineNo++;
    lineLen = strlen(in_Line) - 1;
    if (in_Line[lineLen] == '\n')
      in_Line[lineLen] = '\0';
    else
      in_Line[++lineLen] = '\0';
    if ((nonBlank()) && (in_Line[inCol] != '*'))
    {
      if (!getNum())
        return error("Bad location", lineNo, -1);
      loc = num;
      if (loc > IADDR_SIZE)
        return error("Location too large", lineNo, loc);
      if (!skipCh(':'))
        return error("Missing colon", lineNo, loc);
      if (!getWord())
        return error("Missing opcode", lineNo, loc);

      // Buscar el opcode en opCodeTab[]
      op = opHALT;
      int found = FALSE;
      for (; op <= opJUC; op = (OPCODE)((int)op + 1))
      {
        if (strncmp(opCodeTab[op], word, WORDSIZE) == 0)
        {
          found = TRUE;
          break;
        }
      }
      if (!found)
        return error("Illegal opcode", lineNo, loc);

      switch (opClass(op))
      {
      case opclRR:
        /***********************************/
        if ((!getNum()) || (num < 0) || (num >= NO_REGS))
          return error("Bad first register", lineNo, loc);
        arg1 = num;
        if (!skipCh(','))
          return error("Missing comma", lineNo, loc);
        if ((!getNum()) || (num < 0) || (num >= NO_REGS))
          return error("Bad second register", lineNo, loc);
        arg2 = num;
        if (!skipCh(','))
          return error("Missing comma", lineNo, loc);
        if ((!getNum()) || (num < 0) || (num >= NO_REGS))
          return error("Bad third register", lineNo, loc);
        arg3 = num;
        break;

      case opclRM:
      case opclRA:
        /***********************************/
        if ((!getNum()) || (num < 0) || (num >= NO_REGS))
          return error("Bad first register", lineNo, loc);
        arg1 = num;
        if (!skipCh(','))
          return error("Missing comma", lineNo, loc);
        if (!getNum())
          return error("Bad displacement", lineNo, loc);
        arg2 = num;
        if (!skipCh('(') && !skipCh(','))
          return error("Missing LParen", lineNo, loc);
        if ((!getNum()) || (num < 0) || (num >= NO_REGS))
          return error("Bad second register", lineNo, loc);
        arg3 = num;
        break;
      }
      iMem[loc].iop = op;
      iMem[loc].iarg1 = arg1;
      iMem[loc].iarg2 = arg2;
      iMem[loc].iarg3 = arg3;
    }
  }
  return TRUE;
} /* readInstructions */

/********************************************/
STEPRESULT stepTM(void)
{
  INSTRUCTION currentinstruction;
  int pc;
  int r, s, t, m;

  pc = reg[PC_REG].value.iVal;
  if ((pc < 0) || (pc >= IADDR_SIZE))
  {
    printf("Error: Instruction Memory Fault at address %d\n", pc);
    return srIMEM_ERR;
  }
  currentinstruction = iMem[pc];

  /* Mostrar número de instrucción y detalles */
  printf("Executing instruction at address");
  writeInstruction(pc);

  reg[PC_REG].value.iVal = pc + 1;

  switch (opClass(currentinstruction.iop))
  {
  case opclRR:
    /***********************************/
    r = (int)currentinstruction.iarg1;
    s = (int)currentinstruction.iarg2;
    t = (int)currentinstruction.iarg3;
    break;

  case opclRM:
    /***********************************/
    r = (int)currentinstruction.iarg1;
    s = (int)currentinstruction.iarg3;
    // Modificación para manejar correctamente registros flotantes
    if (s == 0)
      m = (int)currentinstruction.iarg2;
    else if (reg[s].isFloat)
      m = (int)currentinstruction.iarg2 + (int)reg[s].value.fVal;
    else
      m = (int)currentinstruction.iarg2 + reg[s].value.iVal;
    if ((m < 0) || (m >= DADDR_SIZE))
    {
      printf("Error: Data Memory Fault at address %d\n", m);
      return srDMEM_ERR;
    }
    break;

  case opclRA:
    /***********************************/
    r = (int)currentinstruction.iarg1;
    s = (int)currentinstruction.iarg3;
    // Modificación para manejar correctamente registros flotantes
    if (s == 0)
      m = (int)currentinstruction.iarg2;
    else if (reg[s].isFloat)
      m = (int)currentinstruction.iarg2 + (int)reg[s].value.fVal;
    else
      m = (int)currentinstruction.iarg2 + reg[s].value.iVal;
    break;
  } /* switch */

  switch (currentinstruction.iop)
  { /* RR instructions */
  case opHALT:
    /***********************************/
    printf("HALT encountered.\n");
    return srHALT;
    /* break; */

  case opIN:
    /***********************************/
    {
      printf("Enter value (integer or float): ");
      char input[LINESIZE];
      fgets(input, LINESIZE, stdin);
      if (strchr(input, '.'))
      {
        reg[r].value.fVal = atof(input);
        reg[r].isFloat = 1;
      }
      else
      {
        reg[r].value.iVal = atoi(input);
        reg[r].isFloat = 0;
      }
      break;
    }

  case opOUT:
    if (reg[r].isFloat)
    {
      printf("OUT instruction prints: %f\n", reg[r].value.fVal);
    }
    else
    {
      printf("OUT instruction prints: %d\n", reg[r].value.iVal);
    }
    break;
  case opADD:
    if (reg[s].isFloat || reg[t].isFloat)
    {
      reg[r].value.fVal =
          (reg[s].isFloat ? reg[s].value.fVal : reg[s].value.iVal) +
          (reg[t].isFloat ? reg[t].value.fVal : reg[t].value.iVal);

      reg[r].isFloat = 1;
    }
    else
    {
      reg[r].value.iVal = reg[s].value.iVal + reg[t].value.iVal;

      reg[r].isFloat = 0;
    }
    break;
  case opSUB:
    if (reg[s].isFloat || reg[t].isFloat)
    {
      reg[r].value.fVal =
          (reg[s].isFloat ? reg[s].value.fVal : reg[s].value.iVal) -
          (reg[t].isFloat ? reg[t].value.fVal : reg[t].value.iVal);

      reg[r].isFloat = 1;
    }
    else
    {
      reg[r].value.iVal = reg[s].value.iVal - reg[t].value.iVal;

      reg[r].isFloat = 0;
    }
    break;
  case opMUL:
    if (reg[s].isFloat || reg[t].isFloat)
    {
      reg[r].value.fVal =
          (reg[s].isFloat ? reg[s].value.fVal : reg[s].value.iVal) *
          (reg[t].isFloat ? reg[t].value.fVal : reg[t].value.iVal);
      reg[r].isFloat = 1;
    }
    else
    {
      reg[r].value.iVal = reg[s].value.iVal * reg[t].value.iVal;
      reg[r].isFloat = 0;
    }
    break;

  case opDIV:
    /***********************************/
    if ((reg[t].isFloat ? reg[t].value.fVal : reg[t].value.iVal) != 0)
    {
      if (reg[s].isFloat || reg[t].isFloat)
      {
        reg[r].value.fVal =
            (reg[s].isFloat ? reg[s].value.fVal : reg[s].value.iVal) /
            (reg[t].isFloat ? reg[t].value.fVal : reg[t].value.iVal);
        reg[r].isFloat = 1;
      }
      else
      {
        reg[r].value.iVal = reg[s].value.iVal / reg[t].value.iVal;

        reg[r].isFloat = 0;
      }
    }
    else
    {
      printf("Error: Division by zero at instruction %d\n", pc);
      return srZERODIVIDE;
    }
    break;
  case opDVF:
    /***********************************/
    if ((reg[t].isFloat ? reg[t].value.fVal : reg[t].value.iVal) != 0)
    {
      float valDVF = reg[s].isFloat ? reg[s].value.fVal : reg[s].value.iVal;
      float valDVF1 = reg[t].isFloat ? reg[t].value.fVal : reg[t].value.iVal;
      reg[r].isFloat = 1;
      reg[r].value.fVal = valDVF / valDVF1;
    }
    else
    {
      printf("Error: Division by zero at instruction %d\n", pc);
      return srZERODIVIDE;
    }
    break;

  case opLES:
    reg[r].value.iVal = (reg[s].isFloat ? reg[s].value.fVal : reg[s].value.iVal) < (reg[t].isFloat ? reg[t].value.fVal : reg[t].value.iVal);
    reg[r].isFloat = 0;
    break;
  case opGE:
    reg[r].value.iVal = (reg[s].isFloat ? reg[s].value.fVal : reg[s].value.iVal) > (reg[t].isFloat ? reg[t].value.fVal : reg[t].value.iVal);
    reg[r].isFloat = 0;
    break;
  case opLEQ:
    reg[r].value.iVal = (reg[s].isFloat ? reg[s].value.fVal : reg[s].value.iVal) <= (reg[t].isFloat ? reg[t].value.fVal : reg[t].value.iVal);
    reg[r].isFloat = 0;
    break;
  case opGEQ:
    reg[r].value.iVal = (reg[s].isFloat ? reg[s].value.fVal : reg[s].value.iVal) >= (reg[t].isFloat ? reg[t].value.fVal : reg[t].value.iVal);
    reg[r].isFloat = 0;
    break;
  case opEQU:
    reg[r].value.iVal = fabs((reg[s].isFloat ? reg[s].value.fVal : reg[s].value.iVal) - (reg[t].isFloat ? reg[t].value.fVal : reg[t].value.iVal)) < 1e-6;
    reg[r].isFloat = 0;
    break;
  case opNEQ:
    reg[r].value.iVal = fabs((reg[s].isFloat ? reg[s].value.fVal : reg[s].value.iVal) - (reg[t].isFloat ? reg[t].value.fVal : reg[t].value.iVal)) >= 1e-6;
    reg[r].isFloat = 0;
    break;
  case opAND:
    reg[r].value.iVal = (reg[s].isFloat ? reg[s].value.fVal != 0 : reg[s].value.iVal) && (reg[t].isFloat ? reg[t].value.fVal != 0 : reg[t].value.iVal);
    reg[r].isFloat = 0;
    break;
  case opOR:
    reg[r].value.iVal = (reg[s].isFloat ? reg[s].value.fVal != 0 : reg[s].value.iVal) || (reg[t].isFloat ? reg[t].value.fVal != 0 : reg[t].value.iVal);
    reg[r].isFloat = 0;
    break;
  case opNEG:
    reg[r].value.iVal = !(reg[s].isFloat ? reg[s].value.fVal != 0 : reg[s].value.iVal);
    reg[r].isFloat = 0;
    break;
  case opMIN:
    if (reg[s].isFloat)
    {
      reg[r].value.fVal = -reg[s].value.fVal;
      reg[r].isFloat = 1;
    }
    else
    {
      reg[r].value.iVal = -reg[s].value.iVal;
      reg[r].isFloat = 0;
    }
    break;
  case opITF:
    if (reg[s].isFloat)
    {
      reg[r].value.fVal = reg[s].value.fVal;
      reg[r].isFloat = 1;
    }
    else
    {
      reg[r].value.fVal = (float)reg[s].value.iVal;
      reg[r].isFloat = 1;
    }
    break;

  /*************** RM instructions ********************/
  case opLD:
    if (dMem[m].isFloat)
    {
      reg[r].value.fVal = dMem[m].value.fVal;
      reg[r].isFloat = 1;
    }
    else
    {
      reg[r].value.iVal = dMem[m].value.iVal;
      reg[r].isFloat = 0;
    }
    break;
  case opST:
    if (reg[r].isFloat)
    {
      dMem[m].value.fVal = reg[r].value.fVal;
      dMem[m].isFloat = 1;
    }
    else
    {
      dMem[m].value.iVal = reg[r].value.iVal;
      dMem[m].isFloat = 0;
    }
    break;

  /*************** RA instructions ********************/
  case opLDA:
    reg[r].value.iVal = m;
    reg[r].isFloat = 0;
    break;
  case opLDC:
    reg[r].value.iVal = (int)currentinstruction.iarg2;
    reg[r].isFloat = 0;
    break;
  case opLDF:
    reg[r].value.fVal = currentinstruction.iarg2; // Lee un flotante
    reg[r].isFloat = 1;
    break;
  case opJLT:
    if ((reg[r].isFloat ? reg[r].value.fVal : reg[r].value.iVal) < 0)
      reg[PC_REG].value.iVal = m;
    reg[PC_REG].isFloat = 0;
    break;
  case opJLE:

    if ((reg[r].isFloat ? reg[r].value.fVal : reg[r].value.iVal) <= 0)
      reg[PC_REG].value.iVal = m;
    reg[PC_REG].isFloat = 0;
    break;
  case opJGT:
    if ((reg[r].isFloat ? reg[r].value.fVal : reg[r].value.iVal) > 0)
      reg[PC_REG].value.iVal = m;
    reg[PC_REG].isFloat = 0;
    break;
  case opJGE:
    if ((reg[r].isFloat ? reg[r].value.fVal : reg[r].value.iVal) >= 0)
      reg[PC_REG].value.iVal = m;
    reg[PC_REG].isFloat = 0;
    break;
  case opJEQ:
    if (fabs((reg[r].isFloat ? reg[r].value.fVal : reg[r].value.iVal)) < 1e-6)
      reg[PC_REG].value.iVal = m;
    reg[PC_REG].isFloat = 0;
    break;
  case opJNE:
    if (fabs((reg[r].isFloat ? reg[r].value.fVal : reg[r].value.iVal)) >= 1e-6)
      reg[PC_REG].value.iVal = m;
    reg[PC_REG].isFloat = 0;
    break;
  case opJUC:
    reg[PC_REG].value.iVal = m;
    reg[PC_REG].isFloat = 0;
    break;

    /* end of legal instructions */
  default:
    printf("Error: Unknown opcode at instruction %d\n", pc);
    return srIMEM_ERR;
  } /* switch */
  return srOKAY;
} /* stepTM */

/********************************************/
int doCommand(void)
{
  char cmd;
  int stepcnt = 0, i;
  int printcnt;
  int stepResult;
  int regNo, loc;
  do
  {
    printf("Enter command: ");
    fflush(stdin);
    fflush(stdout);
    fgets(in_Line, sizeof(in_Line), stdin);
    lineLen = strlen(in_Line);
    inCol = 0;
  } while (!getWord());

  cmd = word[0];
  switch (cmd)
  {
  case 't':
    /***********************************/
    traceflag = !traceflag;
    printf("Tracing now ");
    if (traceflag)
      printf("on.\n");
    else
      printf("off.\n");
    break;

  case 'h':
    /***********************************/
    printf("Commands are:\n");
    printf("   s(tep <n>      "
           "Execute n (default 1) TM instructions\n");
    printf("   g(o            "
           "Execute TM instructions until HALT or error\n");
    printf("   r(egs          "
           "Print the contents of the registers\n");
    printf("   i(Mem <b <n>>  "
           "Print n iMem locations starting at b\n");
    printf("   d(Mem <b <n>>  "
           "Print n dMem locations starting at b\n");
    printf("   t(race         "
           "Toggle instruction trace\n");
    printf("   p(rint         "
           "Toggle print of total instructions executed"
           " ('go' only)\n");
    printf("   c(lear         "
           "Reset simulator for new execution of program\n");
    printf("   h(elp          "
           "Cause this list of commands to be printed\n");
    printf("   q(uit          "
           "Terminate the simulation\n");
    break;

  case 'p':
    /***********************************/
    icountflag = !icountflag;
    printf("Printing instruction count now ");
    if (icountflag)
      printf("on.\n");
    else
      printf("off.\n");
    break;

  case 's':
    /***********************************/
    if (atEOL())
      stepcnt = 1;
    else if (getNum())
      stepcnt = (int)fabs(num);
    else
      printf("Step count?\n");
    break;

  case 'g':
    stepcnt = 1;
    break;

  case 'r':
    /***********************************/
    for (i = 0; i < NO_REGS; i++)
    {
      if (reg[i].isFloat)
        printf("%1d: %f    ", i, reg[i].value.fVal);
      else
        printf("%1d: %i    ", i, reg[i].value.iVal);

      if ((i % 4) == 3)
        printf("\n");
    }
    break;

  case 'i':
    /***********************************/
    printcnt = 1;
    if (getNum())
    {
      iloc = num;
      if (getNum())
        printcnt = num;
    }
    if (!atEOL())
      printf("Instruction locations?\n");
    else
    {
      while ((iloc >= 0) && (iloc < IADDR_SIZE) && (printcnt > 0))
      {
        writeInstruction(iloc);
        iloc++;
        printcnt--;
      }
    }
    break;

  case 'd':
    /***********************************/
    printcnt = 1;
    if (getNum())
    {
      dloc = num;
      if (getNum())
        printcnt = num;
    }
    if (!atEOL())
      printf("Data locations?\n");
    else
    {
      while ((dloc >= 0) && (dloc < DADDR_SIZE) && (printcnt > 0))
      {
        if (dMem[dloc].isFloat)
          printf("%5d: %5f\n", dloc, dMem[dloc].value.fVal);
        else
          printf("%5d: %5d\n", dloc, dMem[dloc].value.iVal);
        dloc++;
        printcnt--;
      }
    }
    break;

  case 'c':
    /***********************************/
    iloc = 0;
    dloc = 0;
    stepcnt = 0;
    for (regNo = 0; regNo < NO_REGS; regNo++)
    {
      reg[regNo].isFloat = 0;
      reg[regNo].value.iVal = 0;
    }

    dMem[0].isFloat = 0;
    dMem[0].value.iVal = DADDR_SIZE - 1;
    for (loc = 1; loc < DADDR_SIZE; loc++)
    {
      dMem[loc].isFloat = 0;
      dMem[loc].value.iVal = 0;
      dMem[loc].value.fVal = 0.0f;
    }
    break;

  case 'q':
    return FALSE; /* break; */

  default:
    printf("Command %c unknown.\n", cmd);
    break;
  } /* case */
  stepResult = srOKAY;
  if (stepcnt > 0)
  {
    if (cmd == 'g')
    {
      stepcnt = 0;
      while (stepResult == srOKAY)
      {
        iloc = reg[PC_REG].value.iVal;
        if (traceflag)
          writeInstruction(iloc);
        stepResult = stepTM();
        stepcnt++;
      }
      if (icountflag)
        printf("Number of instructions executed = %d\n", stepcnt);

      // Reportar si ocurrió un error durante la ejecución
      if (stepResult != srHALT && stepResult != srOKAY)
      {
        printf("Execution stopped due to error: %s\n",
               stepResultTab[stepResult]);
      }
    }
    else
    {
      while ((stepcnt > 0) && (stepResult == srOKAY))
      {
        iloc = reg[PC_REG].value.iVal;
        if (traceflag)
          writeInstruction(iloc);
        stepResult = stepTM();
        stepcnt--;
      }
      printf("%s\n", stepResultTab[stepResult]);

      // Reportar si ocurrió un error durante la ejecución
      if (stepResult != srOKAY && stepResult != srHALT)
      {
        printf("Execution stopped due to error: %s\n",
               stepResultTab[stepResult]);
      }
    }
  }
  return TRUE;
} /* doCommand */

/********************************************/
/* E X E C U T I O N   B E G I N S   H E R E */
/********************************************/

int main(int argc, char *argv[])
{
  // Deshabilitar el almacenamiento en búfer de la salida estándar
  setvbuf(stdout, NULL, _IONBF, 0);

  if (argc != 2)
  {
    printf("usage: %s <filename>\n", argv[0]);
    exit(1);
  }
  strcpy(pgmName, argv[1]);
  if (strchr(pgmName, '.') == NULL)
    strcat(pgmName, ".tm");
  pgm = fopen(pgmName, "r");
  if (pgm == NULL)
  {
    printf("file '%s' not found\n", pgmName);
    exit(1);
  }

  /* read the program */
  if (!readInstructions())
    exit(1);
  /* switch input file to terminal */
  /* reset( input ); */
  /* read-eval-print */
  printf("TM  simulation (enter h for help)...\n");
  do
    done = !doCommand();
  while (!done);
  printf("Simulation done.\n");
  return 0;
}