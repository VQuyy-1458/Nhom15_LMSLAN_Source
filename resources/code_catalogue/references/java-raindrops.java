import java.util.*;
class RaindropConverter {String convert(int n){String r="";if(n%3==0)r+="Pling";if(n%5==0)r+="Plang";if(n%7==0)r+="Plong";return r.isEmpty()?""+n:r;}}
public class Main {

 static String dump(Object o){
  if(o==null)return "null";
  if(o instanceof String){StringBuilder s=new StringBuilder("\"");for(char c:((String)o).toCharArray()){switch(c){case '"':s.append("\\\"");break;case '\\':s.append("\\\\");break;case '\n':s.append("\\n");break;case '\r':s.append("\\r");break;case '\t':s.append("\\t");break;default:if(c<32)s.append(String.format("\\u%04x",(int)c));else s.append(c);}}return s.append('"').toString();}
  if(o instanceof Boolean)return o.toString();
  if(o instanceof Number){double d=((Number)o).doubleValue();if(!Double.isFinite(d))throw new IllegalArgumentException();return java.math.BigDecimal.valueOf(d).setScale(6,java.math.RoundingMode.HALF_UP).stripTrailingZeros().toPlainString();}
  List<String> pieces=new ArrayList<>();
  if(o instanceof Map){Map<?,?> m=(Map<?,?>)o;for(Object k:m.keySet())pieces.add(dump(k.toString())+":"+dump(m.get(k)));return "{"+String.join(",",pieces)+"}";}
  if(o.getClass().isArray()){for(int i=0;i<java.lang.reflect.Array.getLength(o);i++)pieces.add(dump(java.lang.reflect.Array.get(o,i)));}
  else for(Object x:(Iterable<?>)o)pieces.add(dump(x));
  return "["+String.join(",",pieces)+"]";
 }
 static void emit(Object o){System.out.println(dump(o));}
public static void main(String[]args){Scanner sc=new Scanner(System.in);String s=sc.hasNextLine()?sc.nextLine():"";emit(new RaindropConverter().convert(Integer.parseInt(s)));}}