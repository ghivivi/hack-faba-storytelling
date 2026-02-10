import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * Decipher (decrypt) MyFaba sound tracks<br>
 * Grabs each byte and transforms it following the custom mapping defined.
 * Reverses the encryption applied by MKICipher to restore the original MP3.
 */
public class MKIDecipher {

    private static final List<List<Integer>> byteHighNibble = Arrays.asList(
            Arrays.asList(0x30, 0x30, 0x20, 0x20, 0x10, 0x10, 0x00, 0x00, 0x70, 0x70, 0x60, 0x60, 0x50, 0x50, 0x40, 0x40, 0xB0, 0xB0, 0xA0, 0xA0, 0x90, 0x90, 0x80, 0x80, 0xF0, 0xF0, 0xE0, 0xE0, 0xD0, 0xD0, 0xC0, 0xC0),
            Arrays.asList(0x00, 0x00, 0x10, 0x10, 0x20, 0x20, 0x30, 0x30, 0x40, 0x40, 0x50, 0x50, 0x60, 0x60, 0x70, 0x70, 0x80, 0x80, 0x90, 0x90, 0xA0, 0xA0, 0xB0, 0xB0, 0xC0, 0xC0, 0xD0, 0xD0, 0xE0, 0xE0, 0xF0, 0xF0),
            Arrays.asList(0x10, 0x10, 0x00, 0x00, 0x30, 0x30, 0x20, 0x20, 0x50, 0x50, 0x40, 0x40, 0x70, 0x70, 0x60, 0x60, 0x90, 0x90, 0x80, 0x80, 0xB0, 0xB0, 0xA0, 0xA0, 0xD0, 0xD0, 0xC0, 0xC0, 0xF0, 0xF0, 0xE0, 0xE0),
            Arrays.asList(0x20, 0x20, 0x30, 0x30, 0x00, 0x00, 0x10, 0x10, 0x60, 0x60, 0x70, 0x70, 0x40, 0x40, 0x50, 0x50, 0xA0, 0xA0, 0xB0, 0xB0, 0x80, 0x80, 0x90, 0x90, 0xE0, 0xE0, 0xF0, 0xF0, 0xC0, 0xC0, 0xD0, 0xD0)
    );

    private static final List<List<Integer>> byteLowNibbleOdd = Arrays.asList(
            Arrays.asList(0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF),
            Arrays.asList(0xD, 0xC, 0xF, 0xE, 0x9, 0x8, 0xB, 0xA),
            Arrays.asList(0x1, 0x0, 0x3, 0x2, 0x5, 0x4, 0x7, 0x6),
            Arrays.asList(0x8, 0x9, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF)
    );

    private static final List<List<Integer>> byteLowNibbleEven = Arrays.asList(
            Arrays.asList(0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7),
            Arrays.asList(0x5, 0x4, 0x7, 0x6, 0x1, 0x0, 0x3, 0x2),
            Arrays.asList(0x9, 0x8, 0xb, 0xa, 0xd, 0xc, 0xf, 0xe),
            Arrays.asList(0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7)
    );

    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("Usage: java MKIDecipher <input-file>");
            System.out.println("  <input-file>: Path to the .MKI file to decipher");
            System.out.println("  Output: Creates <input-file>.mp3");
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

        String outputFileName = inputFileName + ".mp3";
        File outputFile = new File(outputFileName);

        try (BufferedInputStream bis = new BufferedInputStream(new FileInputStream(inputFile));
             BufferedOutputStream bos = new BufferedOutputStream(new FileOutputStream(outputFile))) {

            int byteRead;
            int pos = 0;
            while ((byteRead = bis.read()) != -1) {
                // Decipher the byte using reverse transformation
                int modifiedByte = findDecipheredData(pos, byteRead);

                // Write the deciphered byte to the output file
                bos.write(modifiedByte);
                pos++;
            }

            bos.flush();
            System.out.println("File processed successfully. Output file: " + outputFileName);

        } catch (IOException e) {
            System.out.println("An error occurred: " + e.getMessage());
        }
    }

    /**
     * Reverses the cipher transformation to obtain the original byte value.
     * Based on the byte position and the ciphered value, it finds the original byte.
     *
     * @param pos position in the file (used to determine transformation table)
     * @param value the ciphered byte value
     * @return the original (deciphered) byte value
     */
    private static int findDecipheredData(int pos, int value) {
        // Extract high and low nibbles from the ciphered byte
        Integer highByte = (value & 0xF0);
        Integer lowByte = (value & 0x0F);
        int indexHigh = -1;
        int indexLow = -1;

        // Calculate position-based transformation table index
        var posByte = pos % 4;

        // Find indices in transformation tables
        indexHigh = byteHighNibble.get(posByte).indexOf(highByte);
        indexLow = byteLowNibbleEven.get(posByte).indexOf(lowByte);

        // Check if low nibble is in odd table instead
        if (indexLow < 0) {
            indexLow = byteLowNibbleOdd.get(posByte).indexOf(lowByte);
            indexHigh++;
        }

        // Reconstruct the original byte value
        return indexLow * 32 + indexHigh;
    }
}
