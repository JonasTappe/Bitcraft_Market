import os





def run_cleanup_script(s):

    # clean all market_data files
    files = os.listdir(s.base_file_path)
    market_data_files = [f for f in files if f.startswith("market_data_") and f.endswith(".json")]
    keep_only_3_most_recent_files(market_data_files, s)

    # clean all extracted market data files
    extracted_data_files = [f for f in files if f.startswith("extracted_market_data_") and f.endswith(".txt")]
    keep_only_3_most_recent_files(extracted_data_files, s)

    # clean all suitable items data files
    suitable_items_files = [f for f in files if f.startswith("suitable_items_data_") and f.endswith(".json")]
    keep_only_3_most_recent_files(suitable_items_files, s)



def keep_only_3_most_recent_files(filenames, s):
    # keep only the 3 most recent files, delete the rest
    if len(filenames) > s.max_old_files_to_keep:
        # sort files by creation time
        filenames.sort(key=lambda x: os.path.getctime(os.path.join(s.base_file_path, x)))
        files_to_delete = filenames[:-s.max_old_files_to_keep]  # all but the last max_old_files_to_keep
        for f in files_to_delete:
            os.remove(os.path.join(s.base_file_path, f))
        print(f"Deleted {len(files_to_delete)} old files.")