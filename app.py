from shiny import App, Inputs, Outputs, Session, reactive, render, ui
import polars as pl

import plotly.express as px

from shinywidgets import output_widget, render_widget  

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_radio_buttons("radio_timker", "Pilih Timker", choices=["Seluruh Tim Kerja", "Pilih"], selected="Seluruh Tim Kerja"),
        ui.output_ui("input_timker"),
        ui.input_action_button("tampilkan", "Tampilkan"),
        bg="#f8f8f8", 
        open="desktop",
        
    ),  
    ui.img(
        src = "https://bkkbnsulbar.id/wp-content/uploads/2022/12/cropped-logobkkbnsulbar.png", width = "200px", style = "justice-"
    ),
    ui.card(
        ui.card_header(
            "PERSENTASE OUTPUT & ANGGARAN"
        ),
        output_widget("sp_output_realisasi")
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

    output_anggaran = output_anggaran.fill_nan(0)

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
    
    @render_widget
    #@reactive.event(input.action_button)
    def sp_output_realisasi():
        rekap_oa = output_anggaran.group_by(
            "KODE TIMKER"
        ).agg(
            [pl.col("PERSENTASE CAPAIAN").mean().alias("% CAPAIAN").round(2),
            pl.col("PERSENTASE REALISASI ANGGARAN").mean().alias("% ANGGARAN").round(2)]
        )

        if input.radio_timker() == "Seluruh Tim Kerja":
            filter_timker = output_anggaran.select(pl.col("KODE TIMKER").unique())
            filter_timker = filter_timker["KODE TIMKER"].to_list()
        else:
            filter_timker = input.pilihan_timker()

        rekap_oa = rekap_oa.filter(
            pl.col("KODE TIMKER").is_in(filter_timker)
        )

        sulbar = output_anggaran.select(
            pl.col("PERSENTASE CAPAIAN").mean().alias("% CAPAIAN").round(2),
            pl.col("PERSENTASE REALISASI ANGGARAN").mean().alias("% ANGGARAN").round(2)
        )

        # Menambahkan kolom "KODE TIMKER" dengan nilai "Sulbar"
        sulbar = sulbar.with_columns(pl.lit("Sulbar").alias("KODE TIMKER"))

        # Mengatur ulang kolom agar "KODE TIMKER" menjadi kolom pertama
        sulbar = sulbar.select([
            "KODE TIMKER",  # Kolom pertama
            pl.all().exclude("KODE TIMKER")  # Kolom lainnya
        ])

        rekap_oa = pl.concat([sulbar, rekap_oa])

        rekap_oa = rekap_oa.with_columns(
            pl.when(
                pl.col("KODE TIMKER") == "Sulbar"
            )
            .then(pl.lit("Sulbar"))
            .otherwise(
                pl.lit("Timker")
            )
            .alias("color")
        )

        color_map = {
            'Sulbar': 'blue',
            'Timker': 'red'
        }

        fig = px.scatter(rekap_oa, x="% ANGGARAN", y="% CAPAIAN", 
                        text="KODE TIMKER", color="color", 
                        color_discrete_map=color_map,
                        labels={"color": "KELOMPOK"})
        
        fig.update_traces(marker=dict(size=15), textposition='top center')  # Ubah ukuran point
        fig.update_layout(
            plot_bgcolor='white',  # Background plot
            paper_bgcolor='white'  # Background keseluruhan
        )
        # Menambahkan persegi panjang (rectangles) ke dalam layout
        fig.update_layout(
            shapes=[
                # Persegi panjang pertama
                dict(
                    type="rect",
                    x0=50, x1=105,  # Koordinat X untuk persegi panjang
                    y0=50, y1=105,  # Koordinat Y untuk persegi panjang
                    line=dict(color="green"),  # Warna garis tepi
                    fillcolor="lightblue",  # Warna isi
                    opacity=0.2  # Transparansi persegi panjang
                ),
                # Persegi panjang kedua
                dict(
                    type="rect",
                    x0=0, x1=50,  # Koordinat X untuk persegi panjang
                    y0=0, y1=50,  # Koordinat Y untuk persegi panjang
                    line=dict(color="red"),  # Warna garis tepi
                    fillcolor="pink",  # Warna isi
                    opacity=0.2  # Transparansi persegi panjang
                )
            ]
        )
        return fig

app = App(app_ui, server)