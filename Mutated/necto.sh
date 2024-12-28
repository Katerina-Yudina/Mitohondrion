cat mitibase.txt | while read accession; do
  efetch -db nuccore -id "$accession" -format fasta > "${accession}.fasta" || echo "Failed to download $accession" >> errors.log
done

