from shiny import App, Inputs, Outputs, Session, reactive, render, ui
import polars as pl

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_radio_buttons("radio_timker", "Pilih Timker", choices=["Seluruh Tim Kerja", "Pilih"]),
        ui.output_ui("input_timker"),
        ui.input_action_button("tampilkan", "Tampilkan"),
        "Sidebar", 
        bg="#f8f8f8", 
        open="desktop",
        
    ),  
    # ui.img(
    #     src = "https://bkkbnsulbar.id/wp-content/uploads/2022/12/cropped-logobkkbnsulbar.png", widht = "10px"
    # ),
    ui.card(
        
    )
)


def server(input, output, session):
    output_anggaran = pl.read_excel("data/Capaian Output dan Komponen TA.2024.xlsx")
    output_anggaran = output_anggaran.select(pl.exclude(["PERMASALAHAN", "SATUAN CAPAIAN", "PERSENTASE REALISASI ANGGARAN"]))
    output_anggaran = output_anggaran.drop_nulls()
    output_anggaran = output_anggaran.with_columns(
            (pl.when(pl.col('TIM KERJA')=='Hukum, Kepegawaian Umum dan Pelayanan Publik')
                    .then(pl.lit('Hukum, Kepegawaian, Umum dan Pelayanan Publik'))
                    .otherwise(pl.col('TIM KERJA')))
                .alias('TIM KERJA')
                    )
    output_anggaran = output_anggaran.with_columns(
        pl.when(
            pl.col("PERSENTASE CAPAIAN") > 100
        )
        .then(100)
        .otherwise(
            pl.col("PERSENTASE CAPAIAN")
        )
        .alias("PERSENTASE CAPAIAN")
    )
    output_anggaran = output_anggaran.with_columns(
        pl.when(pl.col("TIM KERJA") == "Akses, Kualitas Layanan KB dan Kesehatan Reproduksi")
        .then(pl.lit("KB"))
        .when(pl.col("TIM KERJA") == "Hubungan Antar Lembaga, Advokasi, KIE dan Kehumasan")
        .then(pl.lit("Advokasi"))
        .when(pl.col("TIM KERJA") == "Hukum, Kepegawaian, Umum dan Pelayanan Publik")
        .then(pl.lit("Kepegawaian"))
        .when(pl.col("TIM KERJA") == "Ketahanan Keluarga")
        .then(pl.lit("KS"))
        .when(pl.col("TIM KERJA") == "Keuangan, Anggaran dan Pengelolaan BMN")
        .then(pl.lit("Keuangan"))
        .when(pl.col("TIM KERJA") == "Pelaporan dan Statistik dan Pengelolaan TIK")
        .then(pl.lit("Datin"))
        .when(pl.col("TIM KERJA") == "Pelatihan dan Peningkatan Kompetensi")
        .then(pl.lit("Latbang"))
        .when(pl.col("TIM KERJA") == "Pencegahan Stunting")
        .then(pl.lit("Stunting"))
        .when(pl.col("TIM KERJA") == "Pengelolaan dan Pembinaan Tenaga Lini Lapangan")
        .then(pl.lit("Linlap"))
        .when(pl.col("TIM KERJA") == "Pengendalian Penduduk")
        .then(pl.lit("Dalduk"))
        .when(pl.col("TIM KERJA") == "Perencanaan dan Manajemen Kinerja")
        .then(pl.lit("Perencanaan"))
        .when(pl.col("TIM KERJA") == "ZI WBK/WBBM dan SPIP")
        .then(pl.lit("ZI"))
        .otherwise(pl.lit("D"))
        .alias("KODE TIMKER")
    )

    output_anggaran = output_anggaran.with_columns(
        (pl.col("REALISASI ANGGARAN") / pl.col("PAGU ANGGARAN")*100).alias("PERSENTASE REALISASI ANGGARAN")
    )

    output_anggaran = output_anggaran.with_columns(
        pl.col("PERSENTASE CAPAIAN").round(2),
        pl.col("PERSENTASE REALISASI ANGGARAN").round(2)
    )

    @render.ui
    def input_timker():
        pilihan_timker = output_anggaran.select(pl.col("KODE TIMKER").unique())
        pilihan_timker = pilihan_timker["KODE TIMKER"].to_list()
        #pilihan_timker = output_anggaran.select(pl.col("TIM KERJA").unique()).to_numpy()
        select_timker = ui.input_selectize(
            "pilihan_timker", "Pilih Tim Kerja", 
            choices={
                "": "Pilih Timker",
                "Latbang": "Latbang",
                "Kepegawaian": "Kepegawaian",
                "Advokasi": "Advokasi",
                "Stunting": "Stunting",
                "Dalduk": "Dalduk",
                "Perencanaan": "Perencanaan",
                "KS": "KS",
                "Keuangan": "Keuangan",
                "Datin": "Datin",
                "ZI": "ZI",
                "KB": "KB",
                "Linlap": "Linlap"
            },
            multiple=True,
            options={
                "plugins": ['clear_button']
            }
        )
        return ui.panel_conditional(
            "input.radio_timker == 'Pilih'",
            select_timker
        )
        
    pass


app = App(app_ui, server)