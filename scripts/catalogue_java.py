"""Original reference implementations and API adapters for MIT Exercism exercises.

These files are teacher-side verification assets, never student answer payloads.
"""
import json
import math

def lit(value):
    if isinstance(value,str):return json.dumps(value,ensure_ascii=True)
    if isinstance(value,bool):return str(value).lower()
    if isinstance(value,(int,float)):return repr(value)
    raise ValueError(value)

SERIALIZER=r'''
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
'''
HELPERS='class TriangleException extends Exception{} class BankAccountActionInvalidException extends Exception{} class ValueNotFoundException extends Exception{}'
TEMPLATE='import java.util.*;\n'+HELPERS+"\n{{ STUDENT_ANSWER | replace({'public class ': 'class '}) }}\nclass Main {\n"+SERIALIZER+'\npublic static void main(String[] args) throws Exception {try{\n{{ TEST.testcode }}\n}catch(Exception e){emit("ERROR");}}\n}'

REFS={
'leap':'''class Leap {boolean isLeapYear(int y){return y%400==0||y%4==0&&y%100!=0;}}''',
'difference-of-squares':'''class DifferenceOfSquaresCalculator {int computeSquareOfSumTo(int n){int s=n*(n+1)/2;return s*s;}int computeSumOfSquaresTo(int n){return n*(n+1)*(2*n+1)/6;}int computeDifferenceOfSquares(int n){return computeSquareOfSumTo(n)-computeSumOfSquaresTo(n);}}''',
'hamming':'''class Hamming {String a,b;Hamming(String a,String b){if(a.length()!=b.length())throw new IllegalArgumentException();this.a=a;this.b=b;}int getHammingDistance(){int n=0;for(int i=0;i<a.length();i++)if(a.charAt(i)!=b.charAt(i))n++;return n;}}''',
'raindrops':'''class RaindropConverter {String convert(int n){String r="";if(n%3==0)r+="Pling";if(n%5==0)r+="Plang";if(n%7==0)r+="Plong";return r.isEmpty()?""+n:r;}}''',
'reverse-string':'''class ReverseString {String reverse(String s){return new StringBuilder(s).reverse().toString();}}''',
'pangram':'''class PangramChecker {boolean isPangram(String s){return s.toLowerCase(Locale.ROOT).chars().filter(c->c>='a'&&c<='z').distinct().count()==26;}}''',
'isogram':'''class IsogramChecker {boolean isIsogram(String s){Set<Integer> seen=new HashSet<>();return s.toLowerCase(Locale.ROOT).codePoints().filter(Character::isLetter).allMatch(seen::add);}}''',
'resistor-color':'''class ResistorColor {String[] colors(){return new String[]{"black","brown","red","orange","yellow","green","blue","violet","grey","white"};}int colorCode(String c){return Arrays.asList(colors()).indexOf(c);}}''',
'triangle':'''class Triangle {double a,b,c;Triangle(double a,double b,double c)throws TriangleException{if(a<=0||b<=0||c<=0||a+b<=c||a+c<=b||b+c<=a)throw new TriangleException();this.a=a;this.b=b;this.c=c;}boolean isEquilateral(){return a==b&&b==c;}boolean isIsosceles(){return a==b||a==c||b==c;}boolean isScalene(){return !isIsosceles();}}''',
'complex-numbers':'''class ComplexNumber {double a,b;ComplexNumber(double a,double b){this.a=a;this.b=b;}double getReal(){return a;}double getImaginary(){return b;}double abs(){return Math.hypot(a,b);}ComplexNumber add(ComplexNumber z){return new ComplexNumber(a+z.a,b+z.b);}ComplexNumber subtract(ComplexNumber z){return new ComplexNumber(a-z.a,b-z.b);}ComplexNumber multiply(ComplexNumber z){return new ComplexNumber(a*z.a-b*z.b,a*z.b+b*z.a);}ComplexNumber divide(ComplexNumber z){double d=z.a*z.a+z.b*z.b;return new ComplexNumber((a*z.a+b*z.b)/d,(b*z.a-a*z.b)/d);}ComplexNumber conjugate(){return new ComplexNumber(a,-b);}ComplexNumber exponentialOf(){return new ComplexNumber(Math.exp(a)*Math.cos(b),Math.exp(a)*Math.sin(b));}}''',
'rational-numbers':'''class Rational {int n,d;static int gcd(int a,int b){return b==0?a:gcd(b,a%b);}Rational(int n,int d){if(d==0)throw new IllegalArgumentException();int g=gcd(Math.abs(n),Math.abs(d));this.n=n/g*(d<0?-1:1);this.d=Math.abs(d)/g;}int getNumerator(){return n;}int getDenominator(){return d;}Rational add(Rational r){return new Rational(n*r.d+r.n*d,d*r.d);}Rational subtract(Rational r){return new Rational(n*r.d-r.n*d,d*r.d);}Rational multiply(Rational r){return new Rational(n*r.n,d*r.d);}Rational divide(Rational r){return new Rational(n*r.d,d*r.n);}Rational abs(){return new Rational(Math.abs(n),d);}Rational pow(int p){return p<0?new Rational((int)Math.pow(d,-p),(int)Math.pow(n,-p)):new Rational((int)Math.pow(n,p),(int)Math.pow(d,p));}double exp(double x){return Math.pow(x,(double)n/d);}}''',
'bank-account':'''class BankAccount {boolean opened=false;int balance=0;void open()throws BankAccountActionInvalidException{if(opened)throw new BankAccountActionInvalidException();opened=true;balance=0;}void check()throws BankAccountActionInvalidException{if(!opened)throw new BankAccountActionInvalidException();}void close()throws BankAccountActionInvalidException{check();opened=false;}int getBalance()throws BankAccountActionInvalidException{check();return balance;}void deposit(int n)throws BankAccountActionInvalidException{check();if(n<0)throw new BankAccountActionInvalidException();balance+=n;}void withdraw(int n)throws BankAccountActionInvalidException{check();if(n<0||n>balance)throw new BankAccountActionInvalidException();balance-=n;}}''',
'grade-school':'''class School {TreeMap<Integer,TreeSet<String>> grades=new TreeMap<>();Set<String> names=new HashSet<>();boolean add(String s,int n){if(!names.add(s))return false;grades.computeIfAbsent(n,k->new TreeSet<>()).add(s);return true;}List<String> roster(){List<String> r=new ArrayList<>();for(TreeSet<String> g:grades.values())r.addAll(g);return r;}List<String> grade(int n){return new ArrayList<>(grades.getOrDefault(n,new TreeSet<>()));}}''',
'clock':'''class Clock {int t;Clock(int h,int m){t=Math.floorMod(h*60+m,1440);}void add(int m){t=Math.floorMod(t+m,1440);}public String toString(){return String.format(Locale.ROOT,"%02d:%02d",t/60,t%60);}public boolean equals(Object o){return o instanceof Clock&&t==((Clock)o).t;}public int hashCode(){return t;}}''',
'binary-search':'''class BinarySearch {List<Integer> a;BinarySearch(List<Integer> a){this.a=a;}int indexOf(int v)throws ValueNotFoundException{int l=0,r=a.size()-1;while(l<=r){int m=(l+r)/2;if(a.get(m)==v)return m;if(a.get(m)<v)l=m+1;else r=m-1;}throw new ValueNotFoundException();}}''',
'luhn':'''class LuhnValidator {boolean isValid(String s){s=s.replace(" ","");if(s.length()<2||!s.matches("[0-9]+"))return false;int sum=0;for(int i=s.length()-1,k=0;i>=0;i--,k++){int d=s.charAt(i)-'0';if(k%2==1){d*=2;if(d>9)d-=9;}sum+=d;}return sum%10==0;}}''',
'isbn-verifier':'''class IsbnVerifier {boolean isValid(String s){s=s.replace("-","");if(!s.matches("[0-9]{9}[0-9X]"))return false;int sum=0;for(int i=0;i<10;i++)sum+=(10-i)*(s.charAt(i)=='X'?10:s.charAt(i)-'0');return sum%11==0;}}''',
'rotational-cipher':'''class RotationalCipher {int k;RotationalCipher(int k){this.k=k;}String rotate(String s){StringBuilder r=new StringBuilder();for(char c:s.toCharArray()){if(c>='a'&&c<='z')c=(char)('a'+(c-'a'+k)%26);else if(c>='A'&&c<='Z')c=(char)('A'+(c-'A'+k)%26);r.append(c);}return r.toString();}}''',
'scrabble-score':'''class Scrabble {String s;Scrabble(String s){this.s=s;}int getScore(){int n=0;for(char c:s.toUpperCase(Locale.ROOT).toCharArray()){if("AEIOULNRST".indexOf(c)>=0)n++;else if("DG".indexOf(c)>=0)n+=2;else if("BCMP".indexOf(c)>=0)n+=3;else if("FHVWY".indexOf(c)>=0)n+=4;else if(c=='K')n+=5;else if("JX".indexOf(c)>=0)n+=8;else if("QZ".indexOf(c)>=0)n+=10;}return n;}}''',
'word-count':r'''class WordCount {Map<String,Integer> phrase(String s){Map<String,Integer> m=new TreeMap<>();java.util.regex.Matcher r=java.util.regex.Pattern.compile("[a-z0-9]+(?:'[a-z0-9]+)*").matcher(s.toLowerCase(Locale.ROOT));while(r.find())m.merge(r.group(),1,Integer::sum);return m;}}'''
}

def number(x):
    if not isinstance(x,str):return lit(x)
    # Canonical complex tests use only these three mathematical constants.
    return {'pi':'Math.PI','pi/4':'(Math.PI/4)','ln(2)/2':'(Math.log(2)/2)'}[x]

def complex_value(v):
    if isinstance(v,list):return 'new ComplexNumber('+','.join(number(x) for x in v)+')'
    return 'new ComplexNumber('+number(v)+',0)'

def test_code(slug,c):
    p=c['property'];i=c['input'];L=lit
    if slug=='leap':return f'emit(new Leap().isLeapYear({i["year"]}));'
    if slug=='difference-of-squares':return f'emit(new DifferenceOfSquaresCalculator().'+{'squareOfSum':'computeSquareOfSumTo','sumOfSquares':'computeSumOfSquaresTo','differenceOfSquares':'computeDifferenceOfSquares'}[p]+f'({i["number"]}));'
    if slug=='hamming':return f'emit(new Hamming({L(i["strand1"])},{L(i["strand2"])}).getHammingDistance());'
    if slug in {'raindrops','reverse-string','pangram','isogram','luhn','isbn-verifier'}:
        cls,method,key={'raindrops':('RaindropConverter','convert','number'),'reverse-string':('ReverseString','reverse','value'),'pangram':('PangramChecker','isPangram','sentence'),'isogram':('IsogramChecker','isIsogram','phrase'),'luhn':('LuhnValidator','isValid','value'),'isbn-verifier':('IsbnVerifier','isValid','isbn')}[slug]
        return f'emit(new {cls}().{method}({L(i[key])}));'
    if slug=='resistor-color':return 'emit(new ResistorColor().'+('colors()' if p=='colors' else f'colorCode({L(i["color"])})')+');'
    if slug=='triangle':return 'emit(new Triangle('+','.join(L(v) for v in i['sides'])+').'+{'equilateral':'isEquilateral','isosceles':'isIsosceles','scalene':'isScalene'}[p]+'());'
    if slug=='complex-numbers':
        if p in {'real','imaginary','abs'}:return 'emit('+complex_value(i['z'])+'.'+{'real':'getReal','imaginary':'getImaginary','abs':'abs'}[p]+'());'
        expr=(complex_value(i['z'])+'.'+{'conjugate':'conjugate','exp':'exponentialOf'}[p]+'()') if p in {'conjugate','exp'} else complex_value(i['z1'])+'.'+{'add':'add','sub':'subtract','mul':'multiply','div':'divide'}[p]+'('+complex_value(i['z2'])+')'
        return 'ComplexNumber z='+expr+';emit(new double[]{z.getReal(),z.getImaginary()});'
    if slug=='rational-numbers':
        r=lambda a:'new Rational('+','.join(L(x) for x in a)+')'
        if p=='expreal':return 'emit('+r(i['r'])+'.exp('+L(i['x'])+'));'
        expr=(r(i['r1'])+'.'+{'add':'add','sub':'subtract','mul':'multiply','div':'divide'}[p]+'('+r(i['r2'])+')') if p in {'add','sub','mul','div'} else r(i['r'])+('' if p=='reduce' else '.abs()' if p=='abs' else '.pow('+L(i['n'])+')')
        return 'Rational r='+expr+';emit(new int[]{r.getNumerator(),r.getDenominator()});'
    if slug=='bank-account':
        code='BankAccount b=new BankAccount();Object result=null;'
        for op in i['operations']:
            action=op['operation']
            if action=='balance':code+='result=b.getBalance();'
            elif action in {'open','close'}:code+=f'b.{action}();'
            elif action in {'deposit','withdraw'}:code+=f'b.{action}({op["amount"]});'
            else:raise ValueError('concurrent canonical test requires concurrency harness')
        return code+'emit(result);'
    if slug=='grade-school':
        code='School s=new School();List<Boolean> added=new ArrayList<>();'
        for name,grade in i['students']:code+=f'added.add(s.add({L(name)},{grade}));'
        return code+'emit('+('added' if p=='add' else f's.grade({i["desiredGrade"]})' if p=='grade' else 's.roster()')+');'
    if slug=='clock':
        clock=lambda v:f'new Clock({v["hour"]},{v["minute"]})'
        if p=='equal':return 'emit('+clock(i['clock1'])+'.equals('+clock(i['clock2'])+'));'
        return 'Clock c='+clock(i)+';'+(f'c.add({i["value"]*(1 if p=="add" else -1)});' if p!='create' else '')+'emit(c.toString());'
    if slug=='binary-search':return 'emit(new BinarySearch(Arrays.asList('+','.join(L(v) for v in i['array'])+')).indexOf('+L(i['value'])+'));'
    if slug=='rotational-cipher':return f'emit(new RotationalCipher({i["shiftKey"]}).rotate({L(i["text"])}));'
    if slug=='scrabble-score':return f'emit(new Scrabble({L(i["word"])}).getScore());'
    if slug=='word-count':return f'emit(new WordCount().phrase({L(i["sentence"])}));'
    raise ValueError(slug)

PROGRAMS={'raindrops','reverse-string','scrabble-score'}
def program(slug):
    expr={'raindrops':'new RaindropConverter().convert(Integer.parseInt(s))','reverse-string':'new ReverseString().reverse(s)','scrabble-score':'new Scrabble(s).getScore()'}[slug]
    return 'import java.util.*;\n'+REFS[slug]+'\npublic class Main {\n'+SERIALIZER+'public static void main(String[]args){Scanner sc=new Scanner(System.in);String s=sc.hasNextLine()?sc.nextLine():"";emit('+expr+');}}'

CONTRACTS={
'leap':'Leap.isLeapYear(int year): boolean. Năm nhuận chia hết 400 hoặc chia hết 4 nhưng không chia hết 100.',
'difference-of-squares':'DifferenceOfSquaresCalculator: computeSquareOfSumTo(int n), computeSumOfSquaresTo(int n), computeDifferenceOfSquares(int n), đều trả int. Tính (1+…+n)², 1²+…+n² và hiệu hai giá trị, 0 ≤ n ≤ 100.',
'hamming':'Hamming(String leftStrand, String rightStrand), getHammingDistance(): int. Đếm vị trí khác nhau; hai chuỗi khác độ dài phải ném IllegalArgumentException.',
'pangram':'PangramChecker.isPangram(String sentence): boolean. Kiểm tra có đủ 26 chữ cái ASCII, không phân biệt hoa thường; bỏ ký tự khác.',
'isogram':'IsogramChecker.isIsogram(String phrase): boolean. Không lặp chữ cái khi bỏ qua hoa thường, khoảng trắng và dấu gạch nối.',
'resistor-color':'ResistorColor.colorCode(String color): int, colors(): String[]. Thứ tự màu: black, brown, red, orange, yellow, green, blue, violet, grey, white; mã là vị trí từ 0.',
'triangle':'Triangle(double a,double b,double c) throws TriangleException. Cạnh phải dương và tổng hai cạnh > cạnh thứ ba. isEquilateral(), isIsosceles(), isScalene(): boolean. Tam giác đều cũng là cân. Hệ thống cung cấp TriangleException.',
'complex-numbers':'ComplexNumber(double real,double imaginary); getReal(), getImaginary(), abs(): double; add/subtract/multiply/divide(ComplexNumber): ComplexNumber; conjugate(), exponentialOf(): ComplexNumber. Thực hiện số phức thông thường, exp(a+bi)=exp(a)(cos b+i sin b).',
'rational-numbers':'Rational(int numerator,int denominator); getNumerator(),getDenominator(): int. add/subtract/multiply/divide(Rational), abs(), pow(int): Rational; exp(double x): double trả x^(n/d). Luôn tối giản, mẫu dương; mẫu 0 hoặc chia cho 0 ném IllegalArgumentException.',
'bank-account':'BankAccount: open(),close(),deposit(int),withdraw(int),getBalance(): int. Số dư đầu 0; chưa mở/đã đóng không giao dịch, không mở hai lần, không gửi/rút âm hay rút quá số dư. Ném BankAccountActionInvalidException (hệ thống cung cấp). Bài này kiểm thử giao dịch tuần tự.',
'grade-school':'School.add(String name,int grade): boolean (false nếu tên đã tồn tại ở bất kỳ lớp nào). roster(): List<String> xếp theo khối tăng rồi tên ABC; grade(int): List<String> chỉ khối đó, ABC. Không có học sinh trả danh sách rỗng.',
'clock':'Clock(int hours,int minutes), add(int minutes): void, toString(): HH:mm, equals(Object): boolean. Chuẩn hóa modulo 24 giờ kể cả giờ/phút âm; không có ngày.',
'binary-search':'BinarySearch(List<Integer> sorted); indexOf(int value): int (vị trí từ 0). Mảng tăng dần không trùng; không thấy ném ValueNotFoundException do hệ thống cung cấp. Cài thuật toán tìm kiếm nhị phân.',
'luhn':'LuhnValidator.isValid(String value): boolean. Bỏ dấu cách, cần ít nhất 2 chữ số ASCII, ký tự khác không hợp lệ. Từ phải qua trái nhân đôi mỗi chữ số thứ hai, >9 trừ 9; tổng chia hết 10 là hợp lệ.',
'isbn-verifier':'IsbnVerifier.isValid(String isbn): boolean. Bỏ gạch nối, đúng 10 ký tự; 9 chữ số đầu, ký tự cuối có thể X (=10). Tổng d[i]*(10-i), i=0..9 phải chia hết 11.',
'rotational-cipher':'RotationalCipher(int shiftKey), rotate(String data): String. Dịch vòng chữ cái ASCII 0..25 bước; giữ hoa/thường, giữ nguyên số, khoảng trắng và dấu câu.',
'word-count':"WordCount.phrase(String sentence): Map<String,Integer>. Không phân biệt hoa/thường; từ gồm a-z, 0-9, có thể có dấu nháy đơn bên trong (can't); bỏ dấu nháy bao ngoài, tách theo dấu câu/khoảng trắng.",
'raindrops':'Nộp chương trình Java hoàn chỉnh có class và main. Đọc số nguyên dương n trên một dòng. Nối Pling nếu n chia hết 3, Plang nếu chia hết 5, Plong nếu chia hết 7, theo thứ tự đó; nếu không có, kết quả là chuỗi n. In chuỗi kết quả dưới dạng JSON có nháy kép.',
'reverse-string':'Nộp chương trình Java hoàn chỉnh có main. Đọc một dòng chuỗi ASCII, có thể rỗng. In chuỗi đảo ngược dưới dạng JSON có nháy kép (escape đúng nếu cần). Phiên bản này giới hạn ASCII, không yêu cầu xử lý cụm Unicode.',
'scrabble-score':'Nộp chương trình Java hoàn chỉnh, có thể thiết kế class Scrabble và class Main/J05005 có main. Đọc một dòng từ ASCII, bỏ phân biệt hoa/thường. AEIOULNRST=1, DG=2, BCMP=3, FHVWY=4, K=5, JX=8, QZ=10. In tổng điểm nguyên, từ rỗng có điểm 0.'
}
