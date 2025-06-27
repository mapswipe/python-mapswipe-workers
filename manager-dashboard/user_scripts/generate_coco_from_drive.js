function main() {
    const exportFileName = 'your_coco_export.json';
    const folderId = 'your_public_folder_id';
    const folder = DriveApp.getFolderById(folderId);
    const files = folder.getFiles();

    const images = [];

    let id = 1;
    while (files.hasNext()) {
        const file = files.next();
        const name = file.getName();
        const fileId = file.getId();
        // const url = https://drive.google.com/uc?export=view&id=" + fileId;
        const url = `https://drive.google.com/thumbnail?id=${fileId}&sz=w1000`;
        images.push({
            coco_url: url,
            file_name: name,
            id,
        });
        id += 1;
    }

    const exportContent = JSON.stringify({ images });
    const exportFile = DriveApp.createFile(
        exportFileName,
        exportContent,
        MimeType.PLAIN_TEXT,
    );
    const exportFileUrl = exportFile.getUrl();

    Logger.log(`COCO file available at: ${exportFileUrl}`);
}
