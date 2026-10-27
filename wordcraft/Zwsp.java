import com.ibm.icu.text.BreakIterator;
import com.ibm.icu.util.ULocale;
import java.nio.file.*;
// Same rule as the backend's ThaiLineBreaker (no keep-together terms): ZWSP between Thai words.
public class Zwsp {
  static boolean thai(char c) { return c >= '\u0E01' && c <= '\u0E5B'; }
  public static void main(String[] a) throws Exception {
    for (String line : Files.readAllLines(Path.of(a[0]))) {
      BreakIterator bi = BreakIterator.getLineInstance(new ULocale("th")); bi.setText(line);
      StringBuilder sb = new StringBuilder(); int s = bi.first();
      for (int e = bi.next(); e != BreakIterator.DONE; s = e, e = bi.next()) {
        sb.append(line, s, e);
        if (e < line.length() && thai(line.charAt(e-1)) && thai(line.charAt(e))) sb.append('\u200B');
      }
      System.out.println(sb);
    }
  }
}
