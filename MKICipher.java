import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;

/**
 * Cipher (encrypt) MyFaba sound tracks<br>
 * Grabs each byte and transforms it following the custom mapping defined.
 * The output file will have a .MKI extension appended.
 */
public class MKICipher {

    private final static int[][] byteHighNibble = {
        {0x30, 0x30, 0x20, 0x20, 0x10, 0x10, 0x00, 0x00, 0x70, 0x70, 0x60, 0x60, 0x50, 0x50, 0x40, 0x40, 0xB0, 0xB0, 0xA0, 0xA0, 0x90, 0x90, 0x80, 0x80, 0xF0, 0xF0, 0xE0, 0xE0, 0xD0, 0xD0, 0xC0, 0xC0},
        {0x00, 0x00, 0x10, 0x10, 0x20, 0x20, 0x30, 0x30, 0x40, 0x40, 0x50, 0x50, 0x60, 0x60, 0x70, 0x70, 0x80, 0x80, 0x90, 0x90, 0xA0, 0xA0, 0xB0, 0xB0, 0xC0, 0xC0, 0xD0, 0xD0, 0xE0, 0xE0, 0xF0, 0xF0},
        {0x10, 0x10, 0x00, 0x00, 0x30, 0x30, 0x20, 0x20, 0x50, 0x50, 0x40, 0x40, 0x70, 0x70, 0x60, 0x60, 0x90, 0x90, 0x80, 0x80, 0xB0, 0xB0, 0xA0, 0xA0, 0xD0, 0xD0, 0xC0, 0xC0, 0xF0, 0xF0, 0xE0, 0xE0},
        {0x20, 0x20, 0x30, 0x30, 0x00, 0x00, 0x10, 0x10, 0x60, 0x60, 0x70, 0x70, 0x40, 0x40, 0x50, 0x50, 0xA0, 0xA0, 0xB0, 0xB0, 0x80, 0x80, 0x90, 0x90, 0xE0, 0xE0, 0xF0, 0xF0, 0xC0, 0xC0, 0xD0, 0xD0}
    };

    private final static int[][] byteLowNibbleEven = {
        {0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7},
        {0x5, 0x4, 0x7, 0x6, 0x1, 0x0, 0x3, 0x2},
        {0x9, 0x8, 0xb, 0xa, 0xd, 0xc, 0xf, 0xe},
        {0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7}
    };

    private final static int[][] byteLowNibbleOdd = {
        {0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF},
        {0xD, 0xC, 0xF, 0xE, 0x9, 0x8, 0xB, 0xA},
        {0x1, 0x0, 0x3, 0x2, 0x5, 0x4, 0x7, 0x6},
        {0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF}
    };

    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("Usage: java MKICipher <input-file>");
            System.out.println("  <input-file>: Path to the MP3 file to cipher");
            System.out.println("  Output: Creates <input-file>.MKI");
            return;
        }

        String inputFileName = args[0];
        File inputFile = new File(inputFileName);

        // Check if input file exists
        if (!inputFile.exists()) {
            System.out.println("Error: Input file '" + inputFileName + "' does not exist.");
            System.exit(1);
        }

        if (!inputFile.canRead()) {
            System.out.println("Error: Cannot read input file '" + inputFileName + "'.");
            System.exit(1);
        }

        String outputFileName = inputFileName + ".MKI";
        File outputFile = new File(outputFileName);

        try (BufferedInputStream bis = new BufferedInputStream(new FileInputStream(inputFile));
             BufferedOutputStream bos = new BufferedOutputStream(new FileOutputStream(outputFile))) {

            int byteRead;
            int pos = 0;
            while ((byteRead = bis.read()) != -1) {
                int modifiedByte = 0;
                var bytePos = pos % 4;

                // Apply high nibble transformation based on position
                modifiedByte += byteHighNibble[bytePos][byteRead % 32];

                // Apply low nibble transformation (different for even/odd bytes)
                if (byteRead % 2 == 0) {
                    modifiedByte += byteLowNibbleEven[bytePos][byteRead / 32];
                } else {
                    modifiedByte += byteLowNibbleOdd[bytePos][byteRead / 32];
                }

                // Write the ciphered byte to the output file
                bos.write(modifiedByte);
                pos++;
            }

            bos.flush();
            System.out.println("File processed successfully. Output file: " + outputFileName);

        } catch (IOException e) {
            System.out.println("An error occurred: " + e.getMessage());
        }
    }
}
